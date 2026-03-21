"""
When making the eps_surprises_pipelines.py subclass 
of the baseclass, remember that the endpoint returns a list 
and wrap the list in the subclass fetch() method so the base class 
always receives a dict.
"""