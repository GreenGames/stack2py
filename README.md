Stack2py
========

A library that aims to give all the control to the user and yet be easy to use.

stack2py is a library for accessing the SE API (v2.1). It aims to provide a clean and complete interface to the user, giving them complete control and accessibility.

This library works with the new v2.1 API. Although currently it is incomplete (and in development), it aims to:

  -  Be "Pythonic"
  -  Give the user control over the network connections
  -  Be complete 

Example:  

  1.  Get recently active questions on stackoverflow

    ```python
    >>> import stack2py
    >>> so = stack2py.Site('stackoverflow')
    >>> so.get_questions()
    >>> so.questions # the list of questions
    [Question.....ion ID : 4214385]
    ```
