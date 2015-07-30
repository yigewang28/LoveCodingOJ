import lorun
import os


RESULT_STR = [
    'Accepted',
    'Presentation Error',
    'Time Limit Exceeded',
    'Memory Limit Exceeded',
    'Wrong Answer',
    'Runtime Error',
    'Output Limit Exceeded',
    'Compile Error',
    'System Error'
]

def compileSrc(src_path):
    if src_path.endswith('.c'):
        if os.system('gcc %s -o m'%src_path) != 0:
            print('compile failure!')
            return False
    elif src_path.endswith('.cpp'):
        if os.system('g++ %s -o m'%src_path) != 0:
            print('compile failure!')
            return False
    elif src_path.endswith('.java'):
        if os.system('javac %s'%src_path) != 0:
            print('compile failure!')
            return False
    return True

def runone(p_path, in_path, out_path):
    fin = open(in_path)
    ftemp = open('temp.out', 'w')
    argsList = p_path.split(' ')
    
    runcfg = {
        'args': argsList,
        'fd_in':fin.fileno(),
        'fd_out':ftemp.fileno(),
        'timelimit':2000, #in MS
        'memorylimit':200000, #in KB
    }
    
    rst = lorun.run(runcfg)
    fin.close()
    ftemp.close()
    
    if rst['result'] == 0:
        ftemp = open('temp.out')
        fout = open(out_path)
        crst = lorun.check(fout.fileno(), ftemp.fileno())
        fout.close()
        ftemp.close()
        os.remove('temp.out')
        if crst != 0:
            return {'result':crst}
    
    return rst

def judge(src_path, in_path, out_path):
    if not compileSrc(src_path):
        rst = {}
        rst['result'] = 'Compile Error'
        return rst

    if os.path.isfile(in_path) and os.path.isfile(out_path):
        exec_path = './m'
        if src_path.endswith('.java'):
            os.rename(os.path.abspath('.') + '/media/problems/Solution.class',os.path.abspath('.') + '/Solution.class')
            #os.system('jar cvfm Solution.jar manifest Solution.class')
            #print os.path.abspath('.') + '/Solution.class'
            #exec_path = '/usr/bin/java -jar ./Solution.jar Solution' 
            exec_path='java -Xmx 1024m Solution'
        #print exec_path
        rst = runone(exec_path, in_path, out_path)
        rst['result'] = RESULT_STR[rst['result']]
        if src_path.endswith('.java'):
            os.remove(os.path.abspath('.') + '/Solution.class')
        elif src_path.endswith('.c'):
            os.remove('./m') 
        elif src_path.endswith('.cpp'):
            os.remove('./m') 
        return rst
    else:
        #print('testdata:incompleted')
        os.remove('./m')
        exit(-1)
        
