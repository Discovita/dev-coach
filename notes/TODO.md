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
    ## Phase 1: Port Types, Enums, and API Layer ✅ COMPLETE
    [x] 1.1 Create appearance enums in frontend (`enums/appearance/`)
        - gender.ts, skinTone.ts, hairColor.ts, eyeColor.ts, height.ts, build.ts, ageRange.ts, index.ts
    [x] 1.2 Create types in frontend (`types/`)
        - referenceImage.ts (ReferenceImage, CreateReferenceImageRequest, UpdateReferenceImageRequest)
        - userAppearance.ts (UserAppearance interface)
        - imageGeneration.ts (StartImageChatRequest/Response, ContinueImageChatRequest/Response, SaveImageRequest/Response)
    [x] 1.3 Update User type to include appearance fields
    [x] 1.4 Create API functions in frontend (`api/`)
        - referenceImages.ts (list, create, update, delete, upload)
        - userAppearance.ts (get, update)
        - imageGeneration.ts (startImageChat, continueImageChat, saveGeneratedImage)
    [x] 1.5 Create TanStack Query hooks in frontend (`hooks/`)
        - use-reference-images.ts
        - use-user-appearance.ts
        - use-image-generation.ts
    [x] 1.6 Update authFetch to handle FormData (for file uploads)
    
    ## Phase 2: Update Account Page with Reference Images & Appearance ✅ COMPLETE
    [x] 2.1 Port ReferenceImageSlot component
    [x] 2.2 Port ReferenceImageManager component
    [x] 2.3 Port BadgeSelector component (reusable)
    [x] 2.4 Port appearance selector components (Gender, SkinTone, HairColor, EyeColor, Height, Build, AgeRange)
    [x] 2.5 Port AppearanceSelector container component
    [x] 2.6 Update Account page to include:
        - Reference Images section (5 image slots)
        - Appearance Preferences section (all 7 selectors)
        - Keep existing profile info and logout sections
    
    ## Phase 3: Create Images Page with Generation Workflow ✅ COMPLETE
    [x] 3.1 Add brush icon to public folder (Lucide Brush SVG)
    [x] 3.2 Add "Images" nav item to AuthLayout.tsx sidebar (between IAMs and Account)
    [x] 3.3 Create route file: routes/_authenticated/images/index.tsx
    [x] 3.4 Port IdentitySelector component (simplified - no test user support)
    [x] 3.5 Port scene input components (ClothingInput, MoodInput, SettingInput, SceneInputs)
    [x] 3.6 Port GeneratedImageDisplay component
    [x] 3.7 Create Images page component with workflow:
        - Identity selection dropdown
        - Scene details inputs (clothing, mood, setting)
        - Generate button
        - Generated image display with save/download/regenerate
        - Edit image section with follow-up prompts
    [x] 3.8 Update MobileAuthFooter to include Images nav item
    [x] 3.9 Update Identity type with scene fields (clothing, mood, setting)
    [x] 3.10 Add updateIdentity API function for saving scene details
    [x] 3.11 Add SceneInputs type
    
    ## Phase 4: Testing & Polish
    [ ] 4.1 Test reference image upload flow on Account page
    [ ] 4.2 Test appearance preferences save flow
    [ ] 4.3 Test image generation workflow end-to-end
    [ ] 4.4 Verify mobile responsiveness
    [ ] 4.5 Add loading states and error handling
    
[ ] Update the settings page on the purple one to include the image upload stuff and the body customization stuff
    - This is now covered by Phase 2 above (Account page updates)
[ ] Set the visualization phase to unlock images. 
[ ] Image loading is slow
    - Look into lazy loading, loading one at a time, only loading when the user scrolls to it
[ ] Be able to tile and rearrange the identies on the the identies page on the purple one