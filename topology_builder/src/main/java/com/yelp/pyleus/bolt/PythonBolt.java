package com.yelp.pyleus.bolt;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.logging.Logger;

import com.yelp.pyleus.PythonComponentsFactory;

import backtype.storm.Config;
import backtype.storm.task.OutputCollector;
import backtype.storm.task.ShellBolt;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.IRichBolt;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.tuple.Fields;

public class PythonBolt extends ShellBolt implements IRichBolt {
    protected Map<String, Object> outputFields;
    protected Float tickFreqSecs = null;
    protected String[] localCommand;
    protected String portableInterpreter;

    public PythonBolt(final String... command) {
        super();
        localCommand = Arrays.copyOf(command, command.length);
    }
    
    @Override
    public void prepare(@SuppressWarnings("rawtypes") Map stormConf, TopologyContext context,
    		OutputCollector collector) {
    	
    	try {
    		// Update the field like a barbarian
	    	Field privateCommandField = ShellBolt.class.getDeclaredField("_command");
	    	privateCommandField.setAccessible(true);
	    	privateCommandField.set(this, PythonComponentsFactory.buildCommand(localCommand, portableInterpreter));
	    	
    	} catch(SecurityException ex) {
    		Logger.getGlobal().severe("Can't update the ShellBot command: " + ex);
    	} catch (NoSuchFieldException ex) {
    		// Can happen if ShellBot is updated
    		Logger.getGlobal().severe("ShellBot seems to have been updated: " + ex);
		} catch (IllegalArgumentException ex) {
			// Won't happen
			Logger.getGlobal().severe("Error updating the ShellBot command: " + ex);
		} catch (IllegalAccessException ex) {
			// Like security error
			Logger.getGlobal().severe("Error updating the ShellBot command: " + ex);
		}
    	
    	super.prepare(stormConf, context, collector);
    }
    
    public void setPortableInterpreter(String interpreter) {
    	this.portableInterpreter = interpreter;
    }

    public void setOutputFields(final Map<String, Object> outputFields) {
        this.outputFields = outputFields;
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // Can this condition ever happen?
        if (this.outputFields.size() == 1 && this.outputFields.get("default") == null) {
            declarer.declare(new Fields());
        } else {
            for (Entry<String, Object> outEntry : this.outputFields.entrySet()) {
                String stream = outEntry.getKey();
                @SuppressWarnings("unchecked")
                List<String> fields = (List<String>) outEntry.getValue();
                declarer.declareStream(stream, new Fields(fields.toArray(new String[fields.size()])));
            }
        }
    }

    public void setTickFreqSecs(Float tickFreqSecs) {
        this.tickFreqSecs = tickFreqSecs;
    }

    @Override
    public Map<String, Object> getComponentConfiguration() {
        if (this.tickFreqSecs == null) {
            return null;
        }

        Config conf = new Config();
        conf.put(Config.TOPOLOGY_TICK_TUPLE_FREQ_SECS, this.tickFreqSecs);
        return conf;
    }
}
