import os
import glob
from flask import Flask, render_template, request, send_file, redirect, jsonify
import json
cwd = os.getcwd()
import sys
import pickle
import time
# import datetime
# use folders of generation functions
sys.path.insert(0, cwd + '/CM_generate')
sys.path.insert(0, cwd + '/CM_auxiliary')
sys.path.insert(0, cwd + '/CM_NN_VL')
import CM_GN_harmonise_melody as hrm
import CM_user_output_functions as uof
import zipfile
import shutil

__author__ = 'maxk'

# global harmonisation variables
idiom_name = 'BachChorales'
useGrouping = False
request_code = " "
name_suffix = " "
voiceLeading = "NoVL"
mode_in = 'Auto'

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def purge_old_files(directory_path: str, max_files: int = 500, max_age_days: int = 30) -> None:
    """Delete generated files to avoid filling disk.

    - Removes files older than max_age_days
    - Keeps only the most recent max_files files
    """
    try:
        if not os.path.isdir(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            return
        now = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        files = [
            os.path.join(directory_path, f)
            for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f))
        ]
        # Remove old files first
        for f in files:
            try:
                if now - os.path.getmtime(f) > max_age_seconds:
                    os.remove(f)
            except Exception:
                pass
        # Enforce max file count
        files = [
            os.path.join(directory_path, f)
            for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f))
        ]
        if len(files) > max_files:
            files.sort(key=lambda p: os.path.getmtime(p))  # oldest first
            to_delete = files[: len(files) - max_files]
            for f in to_delete:
                try:
                    os.remove(f)
                except Exception:
                    pass
    except Exception:
        # Never block request due to cleanup
        pass


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def safe_replace(src: str, dst: str) -> None:
    """Atomically replace dst with src if dst exists.

    Windows os.rename fails if dst exists; use os.replace with a fallback.
    """
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        os.replace(src, dst)
    except Exception:
        try:
            if os.path.exists(dst):
                try:
                    os.remove(dst)
                except Exception:
                    pass
            shutil.move(src, dst)
        except Exception as e:
            raise e

@app.route("/")
def index():
    return render_template("index.html")

# Serve bundled vendor assets that live under templates/static/ (legacy layout)
@app.route("/vendor/opensheetmusicdisplay.min.js")
def serve_osmd():
    try:
        local_path = os.path.join(APP_ROOT, 'templates', 'static', 'js', 'opensheetmusicdisplay.min.js')
        return send_file(local_path)
    except Exception:
        # Fallback: 404 to let the browser fail clearly
        return ('', 404)

@app.route("/", methods=['POST'])
def upload():
    # use globals
    global useGrouping
    global request_code
    global idiom_name
    global name_suffix
    global voiceLeading
    global mode_in
    # print('request: ', request)
    # Filter out empty file inputs (some browsers may submit an empty FileStorage)
    raw_files = request.files.getlist("file")
    files = [f for f in raw_files if f and getattr(f, 'filename', None)]
    if len(files) < 1:
        # No usable file provided - redirect back to the index so the UI remains available
        print('No file provided in upload request; redirecting to index')
        return redirect('/')
    target = os.path.join(APP_ROOT, 'server_input_melodies/')
    
    # request_code = datetime.datetime.now().strftime("%I_%M_%S%p_%b_%d_%Y")
    # idiom_name = 'BachChorales'
    # useGrouping = True
    if not os.path.isdir(target):
        os.mkdir(target)
    
    # initialise a subfolder name for melodic inputs
    sub_target = 'melodies_'+request_code
    # make a folder to include input melodies
    if not os.path.isdir(target+sub_target):
        os.mkdir(target+sub_target)
    target = target+sub_target+'/'

    # initialise a subfolder for hamonised output IF many requests are given
    output = 'server_harmonised_output/'
    static_output_1 = 'static/harmonisations'
    static_output_2 = 'templates/static/harmonisations'

    # Ensure output dirs exist and cleanup generated files periodically
    os.makedirs(output, exist_ok=True)
    os.makedirs(static_output_1, exist_ok=True)
    purge_old_files(output)
    purge_old_files(static_output_1)

    # Process only valid files and guard against processing errors
    try:
        for file in files:
            print(file)
            filename = file.filename
            # ignore empty filenames just in case
            if not filename:
                continue
            destination = "/".join([target, filename])
            print(destination)
            file.save(destination)

            melodyFolder = target
            melodyFileName = filename

            # temporary voice-leading mapping
            tmp_vl_string = 'simple'
            if voiceLeading == 'NoVL':
                tmp_vl_string = 'simple'
            elif voiceLeading == 'BBVL':
                tmp_vl_string = 'bidirectional_bvl'
            else:
                print('Unknown VL option!')

            m, idiom = hrm.harmonise_melody_with_idiom(
                melodyFolder,
                melodyFileName,
                idiom_name,
                targetFolder=output,
                mode_in=mode_in,
                use_GCT_grouping=useGrouping,
                voice_leading=tmp_vl_string,
            )
    except Exception as e:
        # Log the exception and redirect back to the index to avoid the browser rendering JSON
        print('Error during harmonisation:', e)
        return redirect('/')
    
    # the output name as produced by chameleon
    initial_output_file_name = m.name+'_'+idiom_name+'.xml'
    # change the name by adding the code
    output_file_name = m.name+name_suffix+'.xml'
    # output_file_name = m.name+'_'+idiom_name+'_'+'grp'+str(int(useGrouping))+'_'+request_code+'.xml'
    safe_replace('server_harmonised_output/'+initial_output_file_name, 'server_harmonised_output/'+output_file_name)
    output_file_with_path = 'server_harmonised_output/'+output_file_name

    # also write midi
    midi_name = m.name+name_suffix+'.mid'
    # midi_name = m.name+'_'+idiom_name+'_'+'grp'+str(int(useGrouping))+'_'+request_code+'.mid'
    output_path = os.path.join(APP_ROOT, 'server_harmonised_output/')
    uof.generate_midi(m.output_stream, fileName=midi_name, destination=output_path)
    output_midi_with_path = output_path+'/'+midi_name

    # copy to static folder for playback/display
    shutil.copy2(output_file_with_path, static_output_1)
    shutil.copy2(output_midi_with_path, static_output_1)

    # prepare response
    #tmp_json = {}
    #tmp_json['initial_output_file_name'] = initial_output_file_name
    #return jsonify(tmp_json)
    return send_file(output_file_with_path, as_attachment=True, download_name=output_file_name)
    #return 'file uploaded successfully'

@app.route("/get_idiom_names", methods=['POST'])
def get_idiom_names():
    # Get all idioms from a single canonical folder
    list_all = glob.glob('trained_idioms/*.pickle')
    list_bl = glob.glob('trained_idioms/bl_*.pickle')
    idiom_names_list = [item for item in list_all if item not in list_bl]
    # idiom_names_list = glob.glob('static/trained_idioms/*.pickle')
    allIdioms = {}
    for i in range( len( idiom_names_list ) ):
        ##########Check here#################
        # idiomName = idiom_names_list[i].split('\\')[-1].split('.')[0] #for Windows
        idiomName = idiom_names_list[i].split(os.sep)[-1].split('.')[0] #for Linux, Mac
        ####################################
        with open(idiom_names_list[i], 'rb') as fp:
            anIdiom = pickle.load(fp)
        #gather all modes and append the Auto
        allModes = list(iter(anIdiom.modes.keys()))
        allModes = ['Auto'] + allModes       
        #append to the dictionary 
        allIdioms[idiomName] = allModes
        
    # return response
    return jsonify(allIdioms)

@app.route("/set_parameters", methods=['POST'])
def set_grouping():
    print('inside set_grouping')
    data = request.get_data()
    dat_json = json.loads(data.decode('utf-8'))
    # use globals
    global useGrouping
    global request_code
    global idiom_name
    global name_suffix
    global voiceLeading
    global mode_in
    useGrouping = dat_json['useGrouping']
    request_code = dat_json['clientID']
    idiom_name = dat_json['idiom_name']
    mode_in = dat_json['mode_name']
    voiceLeading = dat_json['voiceLeading']
    # set mode_in
    name_suffix = '_'+idiom_name+'_'+'grp'+str(int(useGrouping))+'_'+voiceLeading+'_'+request_code
    print('useGrouping: ', useGrouping)
    print('request_code: ', request_code)
    print('idiom_name: ', idiom_name)
    print('mode_in: ', mode_in)
    # prepare response
    tmp_json = {}
    tmp_json['success'] = True
    tmp_json['name_suffix'] = name_suffix
    return jsonify(tmp_json)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8885, debug=True)
