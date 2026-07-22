Helpers for submitting simulation jobs using `basf2` and `IBM Spectrum LSF`. 

Install using:
```
pip install b2-run-sim
```

Simulations are run over multiple model parameters. Output data is organized and includes simulation metadata.

Steering files need to take the following command line arguments:

```
simulation_steering_file.py <decay file path> <output file path> <number of events>
```

```
reconstruction_steering_file.py <simulated events file path> <output file path>
```

Decay file should be specified as a template. i.e. put `{parameter_name}` in place of parameter values.

See `examples` for details.