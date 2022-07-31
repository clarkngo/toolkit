# Maven
	
  apache-maven-3.8.6-bin.tar.gz
  
`tar -xvf archive.tar.gz`

use the --extract (-x) option and specify the archive file name after the f option. 

The -v option will make the tar command more visible and print the names of the files being extracted on the terminal.

# JAVA_HOME

https://mkyong.com/java/how-to-set-java_home-environment-variable-on-mac-os-x/

Set the environment variables here:
```
nano ~/.zshenv
```

Add this:
```
export JAVA_HOME=$(/usr/libexec/java_home)
```

Check:
```
echo $JAVA_HOME
```
Expected result:
```
/Library/Java/JavaVirtualMachines/jdk-16.jdk/Contents/Home  
```
