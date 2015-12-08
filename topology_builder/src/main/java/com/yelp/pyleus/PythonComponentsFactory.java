package com.yelp.pyleus;

import java.util.ArrayList;
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

    private String[] buildCommandUnix(final String module, final Map<String, Object> argumentsMap,
        final String loggingConfig, final String serializerConfig) {

        String[] command = new String[3];

        command[0] = "bash";
        command[1] = "-c";

        StringBuilder strBuf = new StringBuilder();
        // Done before launching any spout or bolt in order to cope with Storm permissions bug
        strBuf.append(String.format("chmod 755 %s; %s", VIRTUALENV_INTERPRETER_UNIX, VIRTUALENV_INTERPRETER_UNIX));
        strBuf.append(String.format(" %s %s", MODULE_OPTION, module));

        if (argumentsMap != null) {
            Gson gson = new GsonBuilder().create();
            String json = gson.toJson(argumentsMap);
            json = json.replace("\"", "\\\"");
            strBuf.append(String.format(" --options \"%s\"", json));
        }

        {
            Map<String, Object> pyleusConfig = new HashMap<String, Object>();
            pyleusConfig.put("logging_config_path", loggingConfig);
            pyleusConfig.put("serializer", serializerConfig);
            Gson gson = new GsonBuilder().create();
            String json = gson.toJson(pyleusConfig);
            json = json.replace("\"", "\\\"");
            strBuf.append(String.format(" --pyleus-config \"%s\"", json));
        }

        command[2] = strBuf.toString();

        return command;
    }

    private String[] buildCommandWindows(final String module, final Map<String, Object> argumentsMap,
            final String loggingConfig, final String serializerConfig) {

    	final List<String> command = new ArrayList<String>();
    	command.add("cmd.exe");
    	command.add("/c");

    	command.add(VIRTUALENV_INTERPRETER_WINDOWS);
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

    private String[] buildCommand(final String module, final Map<String, Object> argumentsMap,
            final String loggingConfig, final String serializerConfig) {

    	if(System.getProperty("os.name").toLowerCase().contains("windows")) {
    		return buildCommandWindows(module, argumentsMap, loggingConfig, serializerConfig);
    	} else {
    		return buildCommandUnix(module, argumentsMap, loggingConfig, serializerConfig);
    	}
    }

    public PythonBolt createPythonBolt(final String module, final Map<String, Object> argumentsMap,
        final String loggingConfig, final String serializerConfig) {

        return new PythonBolt(buildCommand(module, argumentsMap, loggingConfig, serializerConfig));
    }

    public PythonSpout createPythonSpout(final String module, final Map<String, Object> argumentsMap,
        final String loggingConfig, final String serializerConfig) {

        return new PythonSpout(buildCommand(module, argumentsMap, loggingConfig, serializerConfig));
    }
}
