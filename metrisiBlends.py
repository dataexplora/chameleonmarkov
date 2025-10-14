import os, sys
cwd = os.getcwd()
sys.path.insert(0, cwd + '/CM_train')
sys.path.insert(0, cwd + '/CM_blending')
sys.path.insert(0, cwd + '/CM_auxiliary')
import CM_TR_TrainingIdiom_class  # απαιτείται για unpickle
import os, pickle, glob
modes_sum = 0
for p in glob.glob('trained_idioms/*.pickle'):
    with open(p, 'rb') as f:
        idiom = pickle.load(f)
    modes_sum += len(idiom.modes.keys())
print('Total modes S =', modes_sum)
print('Expected blended files =', 12 * (modes_sum ** 2))