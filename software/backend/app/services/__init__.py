"""
Services package.

This package contains all the services that the application uses. These
services are used by the controllers to provide the functionality that the
application offers.

Services utilize the events service to communicate with each other. This
allows for a decoupled architecture where services can be added and removed
without affecting the rest of the application.

Python modules are used to organize the services. Each module contains a
service or a group of related services. The modules behave like namespaces
for the services. Modules also allow services for existing as singletons
within the application.
"""
