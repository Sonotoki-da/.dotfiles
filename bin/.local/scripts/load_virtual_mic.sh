#!/bin/bash

# Check if the sink 'SinkForVirtualMic' exists
if ! pactl list short sinks | grep -q 'SinkForVirtualMic'; then
  # Load the module-null-sink if it doesn't exist
  pactl load-module module-null-sink sink_name=Source sink_properties=device.description="SinkForVirtualMic"
  echo "Loaded module-null-sink"
else
  echo "SinkForVirtualMic already exists"
fi

# Check if the source 'VirtualMic' exists
if ! pactl list short sources | grep -q 'VirtualMic'; then
  # Load the module-virtual-source if it doesn't exist
  pactl load-module module-virtual-source source_name=VirtualMic master=Source.monitor
  echo "Loaded module-virtual-source"
else
  echo "VirtualMic already exists"
fi
