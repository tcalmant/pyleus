package com.yelp.pyleus;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.yelp.pyleus.bolt.PythonBolt;
import com.yelp.pyleus.spout.PythonSpout;

public class PythonComponentsFactory {

    public static final String VIRTUALENV_INTERPRETER_UNIX = "pyleus_venv/bin/python";
    public static final String VIRTUALENV_INTERPRETER_WINDOWS = "pyleus_venv\\Scripts\\python.exe";
    public static final String MODULE_OPTION = "-m";
    
    /**
     * Builds Python arguments for the active operating system
     * 
     * @param pythonArguments Arguments to be given to the Python interpreter
     * @param portablePython Path to a portable interpreter
     * @return The command line as a list
     */
    public static String[] buildCommand(String[] pythonArguments) {
    	return buildCommand(pythonArguments, null);
    }
    
    /**
     * Builds Python arguments for the active operating system
     * 
     * @param pythonArguments Arguments to be given to the Python interpreter
     * @param portablePython Path to a portable interpreter
     * @return The command line as a list
     */
    public static String[] buildCommand(String[] pythonArguments, String portablePython) {
    	
    	// Flag to tell our host OS
    	boolean onWindows = System.getProperty("os.name").toLowerCase().contains("windows");
    	
    	List<String> command = new ArrayList<String>();
    	if(onWindows && portablePython != null && new File(portablePython).exists()) {
    		if(!portablePython.endsWith(".exe")) {
    			// Bad interpreter
    			portablePython = null;
    		}
    	} else {
    		// Not in valid conditions to use a portable Python
    		portablePython = null;
    	}
    	
    	// Set up the interpreter to use
    	String pythonInterpreter = null;
    	if(onWindows) {
    		pythonInterpreter = VIRTUALENV_INTERPRETER_WINDOWS;
    		if(portablePython != null) {
    			pythonInterpreter = portablePython;
    		}
    	} else {
    		pythonInterpreter = VIRTUALENV_INTERPRETER_UNIX;
    	}
    	
    	if(onWindows) {
    		// Use cmd.exe to avoid looking for the exact path to 
    		// the interpreter
    		command.add("cmd.exe");
        	command.add("/c");
        	command.add(pythonInterpreter);
        	
        	// Add all other arguments as is
        	command.addAll(Arrays.asList(pythonArguments));
    	} else {
    		// Use bash on Linux
    		command.add("bash");
    		command.add("-c");
    		
    		// Give all the other arguments in a single string
    		StringBuilder strBuf = new StringBuilder();
    		
    		// Done before launching any spout or bolt in order to cope
    		// with Storm permissions bug
            strBuf.append(String.format("chmod 755 %1$s; %1$s",
            		pythonInterpreter));
            
            
            boolean protectNext = false;
            for(String parameter : pythonArguments) {
            	// Don't forget to separate arguments with a space
            	strBuf.append(' ');
            	
            	if(protectNext)
            		// Starting quote
            		strBuf.append('"');
            	
            	strBuf.append(parameter);
            	
            	if(protectNext)
            		// Ending quote
            		strBuf.append('"');
            
            	// Protect argument given as option or configuration
            	protectNext = parameter.contains("--options") 
            			|| parameter.contains("--pyleus-config");
            }
            
            command.add(strBuf.toString());
    	}
    	
    	return command.toArray(new String[command.size()]);
    }
    
    private String[] buildCommand(final String module, final Map<String, Object> argumentsMap,
            final String loggingConfig, final String serializerConfig) {
    	
    	List<String> command = new ArrayList<String>();
    	
    	command.add(MODULE_OPTION);
    	command.add(module);
    	
    	if (argumentsMap != null) {
            Gson gson = new GsonBuilder().create();
            String json = gson.toJson(argumentsMap);
            json = json.replace("\"", "\\\"");
            command.add("--options");
            command.add(json);
        }

    	{
            Map<String, Object> pyleusConfig = new HashMap<String, Object>();
            pyleusConfig.put("logging_config_path", loggingConfig);
            pyleusConfig.put("serializer", serializerConfig);
            Gson gson = new GsonBuilder().create();
            String json = gson.toJson(pyleusConfig);
            json = json.replace("\"", "\\\"");
            command.add("--pyleus-config");
            command.add(json);
        }
    	
    	return command.toArray(new String[command.size()]);
    }

    public PythonBolt createPythonBolt(final String module,
    		final Map<String, Object> argumentsMap,
    		final String loggingConfig, final String serializerConfig) {

        return new PythonBolt(buildCommand(module, argumentsMap,
        		loggingConfig, serializerConfig));
    }

    public PythonSpout createPythonSpout(final String module,
    		final Map<String, Object> argumentsMap,
    		final String loggingConfig, final String serializerConfig) {

        return new PythonSpout(buildCommand(module, argumentsMap,
        		loggingConfig, serializerConfig));
    }
}
