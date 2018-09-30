import subprocess
import os
import shutil
from shutil import copyfile
 
KLEE_PATH="/home/burak/klee/klee/Release+Asserts/bin"
CC="/home/burak/klee/llvm/Release/bin/clang"
 
KLEE=KLEE_PATH+"/klee"
KLEE_TT=KLEE_PATH+"/ktest-tool"
KLEE_STATS=KLEE_PATH+ "/klee-stats"
 
INCLUDE_DIRS = "-I/home/burak/klee/klee/include"
 
CFLAGS= INCLUDE_DIRS + "-I./ -emit-llvm -c -g"
 
 
class FunctionAttributes:
   
    def __init__ (self, param_name, param_return_type):
        self.name       = param_name
        self.return_type = param_return_type
 
######################################################################
   
def get_name( str ):
    #print str
    if str != '':  
        str = str.split("(")
        temp = str[0].split(" ")
        return temp[1];
 
#gets the return value of the function
def get_return_type( str ):
    if str != '':  
        str = str.split("(")
        temp = str[0].split(" ")
        return temp[0];
 
def get_param_types( str ):
    if str != '':  
#get the part containing parameters
        str = str.split("(")
        params = str[1]
#remove the last ) from parameters
        params = params.replace(")", "")#params[:len(params)-1]
        params = params.replace(";", "")#params[:len(params)-1]
        params = params.lstrip()
        #print( params )
#now seperate them
        args = params.split(",")
 
    return args
 
# This function creates a test file for symbolic execution
# for every function. it also creates files to use for compilation
def create_test_file( filename, prototype, test_folder, is_refactored = False):
 
    print 'Implementation file :' + filename
    implementation_file = open(filename, "r")
    content = implementation_file.read()
    content += "\n"
    content += "\n"
    content += "#include \"klee/klee.h\""
    content += "\n"
    content += "\n"
    content += "const int ARRLEN = (100);\n"
    content += "int main(void) \n"
    content += "{ \n"
 
    param_string = ""
    for param in get_param_types(prototype):
        #content += param + ";\n"
        name = param.split(" ")
        param_string += name[-1] + ","
 
        param_filter = name[-1]
        if '*' in param_filter:
            content += param.replace('*', '') + '[ARRLEN]'+ ";\n"
            param_filter = param_filter.replace('*', '')
            content += "klee_make_symbolic(&{}, sizeof(int)*ARRLEN, \"{}\");\n".format(param_filter,param_filter)
        elif 'size_t' in param:
            content += param + "= ARRLEN;\n"
        else:
            content += param + ";\n"
            content += "klee_make_symbolic(&{}, sizeof(int), \"{}\");\n".format(param_filter,param_filter)
            pass
       
        #content += "klee_make_symbolic(&{}, sizeof({})*ARRLEN, \"{}\");\n".format(param_filter,param_filter,param_filter)
       
    param_string = param_string[:len(param_string)-1]
 
    #if they were pointers, convert them into adresses because
    #we just removed pointer identifers above
    param_string = param_string.replace('*', '')
 
    if get_return_type(prototype) == 'void':
        if is_refactored :
            content += get_name(prototype) + '_refactored'  +"("+ param_string + ");" + "\n"
            content += "return 0;\n"
        else :
            content += get_name(prototype) +"("+ param_string + ");" + "\n"
            content += "return 0;\n"
    else:
        if is_refactored :
            content += "return " + get_name(prototype) + '_refactored'  +"("+ param_string + ");" + "\n"
        else :
            content += "return " + get_name(prototype)  +"("+ param_string + ");" + "\n"
   
    content += "} \n"
 
    #create a folder for each function to keep the files
    func_test_folder = test_folder + "/" + get_name(prototype)
    if not os.path.exists(func_test_folder):
        os.makedirs(func_test_folder)
    else:
        items = os.listdir(func_test_folder)
        for item in items:
            if item.endswith(".c") or item == "makefile" or item.endswith(".bc"):
                os.remove(func_test_folder+ "/" +item)
   
    filename = "test_" + get_name(prototype) + ".c"
    bc_filename = "test_" + get_name(prototype) + ".bc"
 
    f = open(func_test_folder + "/" + filename, "w")   
    f.write(content)
    f.close()
 
    ##generate makefile and invoke recipes
    make_test_cases(filename, func_test_folder, bc_filename, prototype)
    test_cases = extract_test_cases(filename, func_test_folder, bc_filename, prototype)
 
    return test_cases
########################
 
class Param:
    def __init__ (self, param_name, param_type):
        self.name = param_name
        self.type = param_type
 
def get_param_attrs(param_list):
 
    param_names = []
    for param_name in param_list:
        param_name = param_name.strip()
        param_split = param_name.split(' ')
 
        name = param_split[-1]
        type_param = param_name.replace(name, '')
        param_names.append(Param(name, type_param))
       
 
    return param_names
 
class UnitTest:
    def __init__ (self, function_name, return_type):
        self.function_name  = function_name
        self.return_type = return_type
        self.cases = []
 
class TestCase:
    def __init__ (self, param_name, param_type, param_value):
        self.param_name  = param_name
        self.param_type  = param_type
        self.param_value = param_value
 
array_counter = 0
 
def extract_test_cases(filename, location, bc_filename, prototype):
   
    items = os.listdir(location + "/klee-last")
    test_cases = []
 
    for item in items:
        if item.endswith(".ktest"):
            p = subprocess.Popen([KLEE_TT, "--write-ints", item], stdout=subprocess.PIPE ,cwd=location + "/klee-last")
            p.wait()
            out, err = p.communicate()
            test_cases.append(out)
 
    params = get_param_types(prototype)
    param_attrs = get_param_attrs(params)
 
    final_cases = UnitTest(prototype, get_return_type(prototype))
 
 
    namelist = []
    for case in test_cases:
 
        #find out the number of objects inside testcase
        lines = case.splitlines()
        num_of_obj = 0
        for line in lines:
            if 'num objects' in line:
                temp_line = line.replace('num objects:', '')
                temp_line = temp_line.strip()
                num_of_obj = int(temp_line)
 
        print num_of_obj
   
        individual_cases = case.split('num objects: '+ str(num_of_obj))
        individual_cases = individual_cases[-1]
        individual_cases = individual_cases.splitlines()
        individual_cases.pop(0)
 
        cases_for_param = []
        for index in range(0, num_of_obj):
            cases_for_param.append(individual_cases[ (index*3) : (index*3) + 3])
 
        list_cases = []
        for param in param_attrs:
 
            print param.name + ' ' + param.type
 
            for item in cases_for_param:
 
                print item[0]
 
                name = item[0].split('name:')
                name = name[-1].replace('\'', '')
                name = name.strip()
 
                if '*' not in param.name and 'int' in param.type and param.name in item[0]:
 
                    temp_line = item[2].split('data:')
                    temp_line = temp_line[-1]
                    temp_line = temp_line.strip()
                    list_cases.append(TestCase(param.name, param.type, int(temp_line)))
 
                elif param.name.replace('*', '') == name and param.type != 'size_t':
 
                    print 'found !!  ' + param.name + '  '+ name
 
                    test_cases_filtered = []
                    lines = item[2].splitlines()
 
                    cases = []
                    muh_line = ''
 
                    for line in lines:
                        if 'data' in line:
                            temp = line.split('data:')
                            muh_line = temp[-1]
                            muh_line = "".join(muh_line.split())
 
                            cases.append(muh_line)
 
                    char_arrays = []
                    for case in cases:
                        char_array = case.split('\\x')
                        char_array = char_array[1:len(char_array)]
                        char_array[-1] = char_array[-1].replace('\'', '')
                        char_arrays.append(char_array)
 
                    array_list = []
                    for array in char_arrays:
 
                        for x in xrange(0,len(array)):
                            if '@' in array[x]:
                                array[x] = array[x].replace('@', '')
                            elif 'P' in array[x]:
                                array[x] = array[x].replace('P', '')
                            elif '?' in array[x]:
                                array[x] = array[x].replace('?', '')
                            elif '/' in array[x]:
                                array[x] = array[x].replace('/', '')
                            elif '_' in array[x]:
                                array[x] = array[x].replace('_', '')
 
                        ival = []
                        for x in xrange(0,(len(array)/4)):
                            ival.append('0x' + array[4*x] + array[4*x + 1] + array[4*x + 2] + array[4*x + 3])
 
                        c_array = []
                        for val in ival:
                            c_array.append(val + ',')
 
                        c_array[-1] = c_array[-1].replace(',' , '')
 
                        array_def = " { "
                        for item in c_array:
                            array_def += str(item)
                        array_def += '}'
                        array_list.append(array_def)
 
                        list_cases.append(TestCase(param.name, param.type, array_def))
                        print 'cases appended : ' + ' ' + param.name + ' ' + param.type
 
                else:
                    print 'Could not deduce param type ' +  param.name + ' ' + param.type + '\n'
 
 
 
        final_cases.cases.append(list_cases)
 
 
    return final_cases
 
# creates the makefile and invokes required recipes
# to get test cases
def make_test_cases(filename, location, bc_filename, prototype):
   
    content = ""
    content += "KLEE_PATH=/home/burak/klee/klee/Release+Asserts/bin\n"
    content += "CC=/home/burak/klee/llvm/Release/bin/clang\n"
    content += "KLEE=$(KLEE_PATH)/klee\n"
    content += "KLEE_TT=$(KLEE_PATH)/ktest-tool\n"
    content += "KLEE_STATS=$(KLEE_PATH)/klee-stats\n"
    content += "INCLUDE_DIRS = /home/burak/klee/klee/include\n"
    content += "CFLAGS=-I$(INCLUDE_DIRS) -I./ -I../ -emit-llvm -c -g\n"
    content += "OUTPUTNAME=main\n"
    content += "OBJS=" + filename + "\n"
    content += "\n"
    content += "default: all\n"
    content += "\n"
    content += "all: $(OBJS)\n"
    content += "\t$(CC) $(CFLAGS) $(OBJS)\n"
    content += "\n"
    content += ".PHONY: tests\n"
    content += "tests:\n"
    content += "\t$(KLEE) -only-output-states-covering-new -max-time=10  "+ bc_filename +"\n"
    content += "\n"
    content += ".PHONY: clean\n"
    content += "clean:\n"
    content += "\trm *.bc\n"
    content += "\trm -rf klee*\n"
    content += "\n"
 
    f = open(location + "/makefile", "w")  
    f.write(content)
    f.close()
 
    # After creating makefile invoke recipes
    p = subprocess.Popen(["make"], stdout=subprocess.PIPE, cwd=location)
    p.wait()
 
    p = subprocess.Popen(["make", "tests"], stdout=subprocess.PIPE, cwd=location)
    p.wait()
    return
 
 
 
def create_gtest(test_cases, filename_header):
 
    content = ""
    content += '#include <gtest/gtest.h>\n'
    content += '#include <cstring>\n'
    content += '#include \"' + filename_header + '.cpp' + '\"\n'
    content += '#include \"' + filename_header + '_refactored.cpp' +  '\"\n'
    content += '\n'
    content += '\n'
    content += "const int ARRLEN = (100);\n"
 
    for test in test_cases:
        case_id = 0
        for case in test.cases:
           
            content += 'TEST(' + get_name(test.function_name) + 'Test, ' + get_name(test.function_name) + str(case_id) + ')\n'
            content += '{\n'
 
            param_string1 = ""
            param_string2 = ""
 
            found_out_param = False
            for values in case:
                if values.param_name == '*out':
                    found_out_param = True
                    print 'FOUND IT'
 
 
            for values in case:
 
                if values.param_name == '*in' or values.param_name == '*out' :
                    print values.param_name + ' ' + values.param_type
                    print 'type 1'
                    content += '\t' + values.param_type + ' ' + values.param_name.replace('*', '') + '_1[ARRLEN]'
                    content += ' = ' + values.param_value + ';\n'
                    content += '\t' + values.param_type + ' ' + values.param_name.replace('*', '') + '_2[ARRLEN]'
                    content += ' = ' + values.param_value + ';\n'
                    param_string1 += values.param_name.replace('*', '') + '_1 ,'
                    param_string2 += values.param_name.replace('*', '') + '_2 ,'
 
                elif test.return_type == 'void' and values.param_name != 'in' :
                    print values.param_name
                    print 'type 2'
                    content += '\t' + values.param_type + ' ' + values.param_name.replace('*', '') + '_1'
                    content += ' = ' + str(values.param_value) + ';\n'
                    content += '\t' + values.param_type + ' ' + values.param_name.replace('*', '') + '_2'
                    content += ' = ' + str(values.param_value) + ';\n'
                    param_string1 += values.param_name.replace('*', '') + '_1 ,'
                    param_string2 += values.param_name.replace('*', '') + '_2 ,'
 
                else:
                    print values.param_name + ' ' + values.param_type
                    print 'type 1'
                    content += '\t' + values.param_type + ' ' + values.param_name.replace('*', '') + '_1[ARRLEN]'
                    content += ' = ' + values.param_value + ';\n'
                    content += '\t' + values.param_type + ' ' + values.param_name.replace('*', '') + '_2[ARRLEN]'
                    content += ' = ' + values.param_value + ';\n'
                    param_string1 += values.param_name.replace('*', '') + '_1 ,'
                    param_string2 += values.param_name.replace('*', '') + '_2 ,'
                    print 'Something\'s wrong  ' + values.param_name + ' ' + values.param_type
 
            param_string1 = param_string1[:len(param_string1)-1]
            param_string2 = param_string2[:len(param_string2)-1]
 
            param_string1 += ', ARRLEN'
            param_string2 += ', ARRLEN'
 
            func_org      = get_name(test.function_name) + '(' + param_string1 + ')'
            func_refactored = get_name(test.function_name) + '_refactored' + '(' + param_string2 + ')'
 
            content += '\t' + func_org + ';\n'
            content += '\t' + func_refactored + ';\n'
 
            if test.return_type == 'void' and found_out_param == False:
                #content += '\tASSERT_EQ(' + values.param_name.replace('*', '') + '_1' + ',' + values.param_name.replace('*', '') + '_1' + ');\n'
                content += '\tEXPECT_TRUE( 0 == std::memcmp( in_1, in_2, sizeof(int)*ARRLEN ) );\n'
                content += '}\n\n'
            elif test.return_type == 'void' and found_out_param == True:
                content += '\tEXPECT_TRUE( 0 == std::memcmp( out_1, out_2, sizeof(int)*ARRLEN ) );\n'
                content += '}\n\n'
            else:
                content += '\tASSERT_EQ('+ func_org + ',' + func_refactored + ');\n'
                content += '}\n\n'
 
            case_id = case_id + 1
       
 
    content += '\n'
    content += 'int main(int argc, char **argv) {\n'
    content += 'testing::InitGoogleTest(&argc, argv);\n'
    content += 'return RUN_ALL_TESTS();\n'
    content += '}'
 
    #assert(0)
 
    return content
 
 
 
##################################   MAIN ROUTINE  #############################################
component_name = "functions"
 
filename_header = component_name + ".h"
filename_imp    = component_name + ".c"
test_folder     = "./" + component_name+ "_test_cases"
 
# make the folder ready
if not os.path.exists(test_folder):
    os.makedirs(test_folder)
else:
    shutil.rmtree(test_folder)
    os.makedirs(test_folder)
 
# copy the header to the test folder for compilation
copyfile(filename_header, test_folder+"/"+filename_header)
copyfile(component_name + "_refactored.h", test_folder+"/"+ component_name + "_refactored.h")
#cpp for gtest
copyfile(filename_imp, test_folder+"/"+component_name + ".cpp" )
copyfile(component_name + "_refactored.c", test_folder+"/"+component_name + "_refactored.cpp" )
 
# run ctags and get the function prototypes
ctag_command = "ctags -x --c-types=+p " + filename_header
function_prototypes = subprocess.check_output(ctag_command, shell=True)
function_prototypes = function_prototypes.split('\n')
 
#
function_list = []
test_cases = []
 
org_case = []
refac_case = []
 
for line in function_prototypes:
    if line != '' and "prototype" in line:     
        line_split = line.split(filename_header); #split the ctag result
        line_split = line_split[-1] # get the part with prototype
        line_split = line_split.strip() #remove any blanks around
        function_list.append(line_split) #keep them in a list for further usage, TODO : REMOVE SOON
 
        org_case = create_test_file(filename_imp, line_split, test_folder);
        refac_case = create_test_file(component_name + "_refactored.c", line_split, test_folder, True)
        cases = org_case.cases + refac_case.cases
       
        total_cases = UnitTest(org_case.function_name, org_case.return_type)
        total_cases.cases = cases
       
        test_cases.append(total_cases)
 
 
test_file = create_gtest(test_cases, component_name)
 
#cpp because of gtest
f = open(test_folder+'/tests.cpp', "w")
f.write(test_file)
f.close()
 
f = open(test_folder+'/CMakeLists.txt', "w")
 
CMakeLists_content = """
cmake_minimum_required(VERSION 2.6)
 
set ( CMAKE_CXX_STANDARD 11 )
set ( CMAKE_CXX_STANDARD_REQUIRED ON )
 
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-narrowing -Wno-fpermissive -Wno-all ")
 
# Locate GTest
find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})
 
# Link runTests with what we want to test and the GTest and pthread library
add_executable(runTests tests.cpp)
target_link_libraries(runTests ${GTEST_LIBRARIES} pthread)
"""
 
f.write(CMakeLists_content)
f.close()
 
p = subprocess.Popen(['cmake', 'CMakeLists.txt'], stdout=subprocess.PIPE, cwd='./' + test_folder)
p.wait()
 
out, err = p.communicate()
 
print out
print err
 
p = subprocess.Popen(['make'], stdout=subprocess.PIPE, cwd='./' + test_folder)
p.wait()
 
out, err = p.communicate()
 
print out
print err
 
p = subprocess.Popen(['./runTests'], stdout=subprocess.PIPE, cwd='./' + test_folder)
p.wait()
 
out, err = p.communicate()
 
print out
print err