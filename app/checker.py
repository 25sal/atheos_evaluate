import os
import glob
from app.config import Config
import logging
logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.ERROR)
import subprocess


class Checker:
    checker={}
    checks = {}

    def append_check(self,label, value):
        if label not in self.checks.keys():
            self.checks[label]=value
        else:
            self.checks[label] +=value
    
    def set_check(self,label, value):
        self.checks[label] =value

    def __init__(self, username, lang, exercise):
        self.checker['vhdl'] = self.vhdl_checker
        self.checker['c'] = self.c_checker
        self.checker['cpp'] = self.c_checker
        self.username = username
        self.lang = lang
        self.exercise = exercise


    def check(self, lang, user_folder, ex_folder ):
        self.checks = {}
        return self.checker[lang](user_folder, ex_folder)

    def vhdl_checker(self, user_folder, ex_folder):
        pass

    def api_checker(self, user_folder, ex_folder):
        result = self.c_builder(user_folder, ex_folder)
        build_logs = result[1]
        ret = result[0]
        if ret == 0:
            test_logs = '\nTesting:\n'
            exec_logs = ''
            file_list = glob.glob(Config.data_dir+"/exercises/"+ex_folder+"/*.in")
            ti = 0
            if not os.path.isdir(user_folder+"/../sandbox"):
                os.mkdir(user_folder+"/../sandbox", 0o0700);
                # il numero di test in cui il file output.bin viene creato
            outfile_passed=0
            for file_in in file_list:
                ti += 1
                test_logs += '+++++++TEST  '+str(ti)+"++++ \n"
                os.system('cp '+file_in+' '+user_folder+'/input.txt')
                #system('cp '.$dir.'/* '.$users_dir.'/test');
                #system('docker exec  --workdir /test wwwtest /test/main');
                #cmd_array = [Config.data_dir+'/mbox/mbox', '-i', '-s', '-n', '-r', '../sandbox', './main']
                #in docker no mbox
                cmd_array = ['./main.exe']
                cprocess = subprocess.run(cmd_array, cwd=user_folder, timeout=5, capture_output=True)
                exec_logs += cprocess.stdout.decode("utf8")
                exec_logs += cprocess.stderr.decode("utf8")
                exec_logs +='\n-------------------------------------------\n'
                #ret_val = os.system('cd '+user_folder+';timeout -s 9 10 '+Config.data_dir+'/mbox/mbox -i -s -n -r ../sandbox  ./main > /dev/null')
                ret_val = cprocess.returncode
                if ret_val == 0:
                    self.set_check("execution", 1)
                    if os.path.isfile(user_folder+'/output.bin'):
                        self.set_check("outfile", 1)
                        outfile_passed += 1
                        cmd_array = [Config.data_dir+"/exercises/"+ex_folder+'/checker', file_in+'_out']
                        cprocess = subprocess.run(cmd_array, cwd=user_folder, timeout=5, capture_output=True)
                        ret_val = cprocess.returncode
                        test_logs += cprocess.stdout.decode("utf8")
                        test_logs += cprocess.stderr.decode("utf8")
                        os.system('rm '+user_folder+'/output.bin');                     
                    elif outfile_passed == 0:
                        self.set_check("outfile", outfile_passed)
                        #comment if the mbox -s option is used
                        #system('cp '+user_folder+'/../sandbox/'+user_folder+'/output.bin '+user_folder+'/' )
                        
                        
            #system('rm -r '.$dir.'/../sandbox/*')
            print(Config.data_dir+"/exercises/"+ex_folder+'/template/input.txt')
            if os.path.isfile(Config.data_dir+"/exercises/"+ex_folder+'/template/input.txt'):
                os.system('cp '+Config.data_dir+"/exercises/"+ex_folder+'/input.txt '+user_folder+'/input.txt')

        else:
            self.set_check("built", 0)
            self.set_check("execution", 0)
            self.set_check("outfile", 0)

        passed = test_logs.count('TEST_SUPERATO')
        failed = test_logs.count('NON_SUPERATO')

        self.set_check("test", passed)    
        return [build_logs,exec_logs, test_logs, passed, failed]

    def c_checker(self, user_folder, ex_folder):
        result_file = user_folder+"/result.log"
        ret_string = ""
        passed = 0
        failed = 0
        with open(result_file, "w") as fd:
            if self.lang == 'c':
                command = 'gcc'
            else:
                command = 'g++'
            fd.write(command+' -o main main.'+self.lang+'\n')
            logging.debug("building: "+command+' -o main main.'+self.lang+'\n')
            cmd_array = [command, '-o', 'main', 'main.'+self.lang]
            cprocess = subprocess.run(cmd_array, cwd=user_folder, capture_output=True)
            ret_val = cprocess.returncode
            ret_string += cprocess.stdout.decode("utf8")
            if ret_val == 0:
                ret_string += 'build ok\n'
                # db.savechecks(self.username, "built", 1,self.exercise)
                self.append_check("built", 1)
                ret_string += 'Testing:\n'
                file_list = glob.glob(ex_folder+"/*.in")
                ti = 0
                if not os.path.isdir(user_folder+"/../sandbox"):
                    os.mkdir(user_folder+"/../sandbox", 0o0700);
                    # il numero di test in cui il file output.bin viene creato
                outfile_passed=0
                for file_in in file_list:
                    ti += 1
                    ret_string += '+++++++TEST  '+str(ti)+"++++ \n"
                    os.system('cp '+file_in+' '+user_folder+'/input.txt')
                    #system('cp '.$dir.'/* '.$users_dir.'/test');
                    #system('docker exec  --workdir /test wwwtest /test/main');
                    #cmd_array = [Config.data_dir+'/mbox/mbox', '-i', '-s', '-n', '-r', '../sandbox', './main']
                    #in docker no mbox
                    cmd_array = ['./main']
                    cprocess = subprocess.run(cmd_array, cwd=user_folder, timeout=5)
                    #ret_val = os.system('cd '+user_folder+';timeout -s 9 10 '+Config.data_dir+'/mbox/mbox -i -s -n -r ../sandbox  ./main > /dev/null')
                    ret_val = cprocess.returncode
                    if ret_val == 0:
                        self.append_check("execution", 1)
                        # db.savechecks(self.username, "execution", 1, self.exercise)
                        #use user_folder./ output.bin if the mbox with -s option is used
                        # if (file_exists($dir.'/../sandbox/'.$dir.'/output.bin'))
                        if os.path.isfile(user_folder+'/output.bin'):
                            # db.savechecks(self.username, "outfile", 1, self.exercise)
                            outfile_passed += 1
                        elif outfile_passed == 0:
                            self.append_check("outfile", outfile_passed)
                            #comment if the mbox -s option is used
                            #system('cp '+user_folder+'/../sandbox/'+user_folder+'/output.bin '+user_folder+'/' )
                            ret_val = os.system('cd '+user_folder+';'+ex_folder+'/checker  '+file_in+'_out >> '+result_file)

                        else:
                            self.append_check("execution", 1)
                            self.append_check("outfile", 1)
                        #system('rm -r '.$dir.'/../sandbox/*');
                if os.path.isfile(Config.data_dir+"/exercises/"+ex_folder+'/template/input.txt'):
                        os.system('cp '+Config.data_dir+"/exercises/"+ex_folder+'/input.txt '+user_folder+'/input.txt')

            else:
                ret_string += cprocess.stderr.decode('utf8')
                self.append_check("built", 0)
                self.append_check("execution", 0)
                self.append_check("outfile", 0)


        with  open(result_file, "r") as dfile:

            for line in dfile:
                if  "TEST_SUPERATO" in line:
                    passed += 1
                if "NON_SUPERATO" in line:
                    failed += 1;

            dfile.close()

        self.append_check("test", passed)

        return [ret_string, passed,failed]

    
    def c_builder(self, user_folder, ex_folder):

        cmd_array = ["git", "commit", "-a", "-m", "build"]
        cprocess = subprocess.run(cmd_array, cwd=user_folder)

        if self.lang == 'c':
            command = 'gcc'
        else:
            command = 'g++'
        logs = command + ' -o main main.' + self.lang + '\n'
        logging.debug("building: " + command + ' -o main main.' + self.lang + '\n')
        cmd_array = [command, '-o', 'main.exe', 'main.' + self.lang]
        cprocess = subprocess.run(cmd_array, cwd=user_folder, capture_output=True)
        ret_val = cprocess.returncode
        logs += cprocess.stdout.decode("utf8")
        logs += cprocess.stderr.decode("utf8")
        if ret_val == 0:
            logs += 'build ok\n'
            self.set_check("built", 1)
        else:
            self.set_check("built", 0)
        return [ret_val,logs]
