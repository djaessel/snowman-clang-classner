# snowman-clang-classner
This is a project based around the snowman decompiler to make it easier to restructure the original C++ source code

To execute, simply use the following command:

```
python py_proj/main.py <cpp_filename>
```  
or  
```  
run_py_classner.sh
```  

Alternatively you could compile the cpp_proj (C++ Project Version).  
After you successfully compiled it, you can run it with the following command:
```  
run_cpp_classner.sh
```  
or if this does not automatically find your executable search for it in the build folder.  
  
# "Dependencies"
## snowman Decompiler
The cpp file should be decompiled output from snowman decompiler.  
> [snowman Decompiler repo](https://github.com/yegord/snowman)  

# snowman with Classner Extension  
Now there also is a modified repo version of snowman with Classner (this project) already included as extension.  
> [snowman Decompiler Classner repo](https://github.com/djaessel/snowman)  

So you could simply use this version of snowman to automate the whole process and directly get the result from snowman itself.  
The procedure is the same as with usual console decompile process of snowman (with the nocode executable).  
The GUI version of snowman might not be supported yet.  
  
Depending on the development state, it is possible that the snowman extension version is not up-to-date at times.  
Keep that in mind, if you are an early adapter or up for experiments that is.  
