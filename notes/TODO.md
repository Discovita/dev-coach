# TODO List

[x] GTKY Phase is taking forever
    - Fixed in prompt V4: Added explicit single-question rule (one ? per response), minimum depth requirement (2 exchanges per topic), and concrete good/bad examples
[x] Warmup Phase examples need to be simpler
    - Fixed in prompt V10: Added simple examples (father, mother, friend, etc.), negative examples (not job titles, temporary states), "ask until done" approach with varied follow-ups
[x] Show Identity Bulletin on the Anything Missing Phase
[x] Identity statements need gramatical rules
    - https://loom.com/share/318ee38531cf49f8affc66ad07e41b2e
    - Fixed in i_am_statement prompt V18: Added critical grammar rules - multiple short sentences each starting with "I" instead of complex participial phrases
[x] Update the body customization stuff to be specific based on the users gender. Custom options for men and women (and person)
    ## Implementation Plan (Option 2: Extended Enum)
    Extend the Build enum with gender-specific values. Frontend filters which options to show based on selected gender.
    No new model fields, no migrations needed.
    
    ### Backend
    [x] 1. Extend Build enum (`server/enums/appearance/build.py`) with gender-specific values:
        - Keep: slim, athletic, average, stocky, large
        - Add male: muscular
        - Add female: curvy, petite, full_figured
    [x] 2. Update CoreViewSet enums endpoint to return build options grouped by gender:
        - `builds_male`: [slim, athletic, average, muscular, stocky, large]
        - `builds_female`: [petite, slim, athletic, average, curvy, full_figured]
        - `builds_neutral`: [slim, athletic, average, stocky, large, heavyset]
    
    ### Frontend
    [x] 3. Update TypeScript Build enum to match backend
    [x] 4. Update BuildSelector to filter options based on selected gender
    [x] 5. Clear build selection if user changes gender and current build isn't valid for new gender
[ ] Create the image generation tool on the purple one
[ ] Update the settings page on the purple one to include the image upload stuff and the body customization stuff
[ ] Set the visualization phase to unlock images. 
[ ] Image loading is slow
    - Look into lazy loading, loading one at a time, only loading when the user scrolls to it
[ ] Be able to tile and rearrange the identies on the the identies page on the purple one