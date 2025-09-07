# Overview

Basic requirements:

- Add a single parameter to the CoachResponse
- This will accept an enum of component names
  - Each component name will have a set of responses.
    - For example, in the Introduction Phase, it'd be good to use this as canned responses for the user to choose from when the Coach asks all those questions. The options would be something like:
    ```text
    Does that make sense?
    [Yes] [No] [Tell me more please]
    ```
    - Clicking each of these options would have some sort of effect on the back end. 
    - These for example would submit a user response based on the button clicked. 
    - There would be other options as well, such as connecting it to an action.
        - We'd have to figure out how to plug that into the action handler. 
            - One way we could do this would be to create separate actions for asking the user to accept their identity, and another for actually accepting it thats connected to the front end component. We could add a special endpoint in the Action ViewSet that would perform the actual action so these components could interface with it. 
        - The user could do things like accept an identity