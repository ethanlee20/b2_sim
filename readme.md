After setting up your environment, run using

```
python3.14 <script> 
```

Steering files need to take the following command line arguments

```
simulation_steering_file.py <decay file path> <output file path> <number of events>
```

```
reconstruction_steering_file.py <simulated events file path> <output file path>
```

Decay file should be specified as a template. i.e. put `{parameter_name}` in place of parameter values.

See `example.py` script and `example` directory for more details.