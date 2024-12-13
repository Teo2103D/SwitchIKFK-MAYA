import maya.cmds as cmds

def create_group_based_on_selection():
    # List of words for each category
    arm_list = ["wrist", "hand", "elbow", "arm", "shoulder", "clavicle", "wrist", "elbow", "shoulder", "arm", "forearm", "hand", "clavicle"]
    leg_list = ["hip", "pelvis", "femur", "kneecap", "knee", "leg", "ankle", "foot", "tibia", "leg", "hip", "knee", "ankle", "pelvis", "waist", "hinge", "foot", "heel", "toe"]

    # Get the selected objects
    selected_objects = cmds.ls(selection=True)
    
    # Check if any objects are selected
    if len(selected_objects) == 0:
        cmds.error("Please select at least one object.")
        return

    # Function to check if a word from a list is present in the object name
    def contains_word(obj_name, word_list):
        for word in word_list:
            if word.lower() in obj_name.lower():  # Check case-insensitively
                return True
        return False

    # Function to determine if an object contains "IK" or "FK"
    def detect_ik_fk(obj_name):
        if "ik" in obj_name.lower():
            return "IK"
        elif "fk" in obj_name.lower():
            return "FK"
        else:
            return None

    # Initialize flags for the groups
    is_arm = None  # None means no group has been determined yet
    is_leg = None  # None, similar to is_arm, for the leg
    group_type = None  # To determine if the objects belong to "IK" or "FK"

    # Analyze each selected object and check which group it belongs to
    for obj in selected_objects:
        if contains_word(obj, arm_list):
            if is_arm is None:
                is_arm = True  # Set the "arm" group for the first time
            elif is_leg is True:
                cmds.error("The selection contains objects from both the 'arm' and 'leg' groups.")
                return
        elif contains_word(obj, leg_list):
            if is_leg is None:
                is_leg = True  # Set the "leg" group for the first time
            elif is_arm is True:
                cmds.error("The selection contains objects from both the 'arm' and 'leg' groups.")
                return
        else:
            cmds.error(f"The object '{obj}' does not belong to any valid group ('arm' or 'leg').")
            return

        # Check if the object contains "IK" or "FK"
        detected_group = detect_ik_fk(obj)
        if detected_group:
            if group_type is None:
                group_type = detected_group
            elif group_type != detected_group:
                cmds.error("The selection contains objects from both the 'IK' and 'FK' groups.")
                return

    # Check if the selection is from only one group
    if is_arm and is_leg:
        cmds.error("The selection contains objects from both the 'arm' and 'leg' groups.")
        return
    elif is_arm is None and is_leg is None:
        cmds.error("No valid objects in the selection ('arm' or 'leg').")
        return

    # Create the locators based on the detected groups
    create_locators_by_suffix_and_order(is_arm, is_leg, selected_objects, group_type)

def create_locators_by_suffix_and_order(is_arm, is_leg, selected_objects, group_type):
    # Counters for each suffix
    counters = {'_L': 0, '_R': 0, '': 0}
    
    # Prefix based on the group
    prefix = ""
    if is_arm:
        prefix = "Arm_"  # If the group is "arm"
    elif is_leg:
        prefix = "Leg_"  # If the group is "leg"
    
    # Determine the locator prefix based on the detected group
    locator_prefix = "FK" if group_type == "IK" else "IK"
    
    # Loop through each selected object
    for selected_object in selected_objects:
        # Detect the suffix (_L, _R, or none)
        if selected_object.endswith("_L"):
            suffix = "_L"
        elif selected_object.endswith("_R"):
            suffix = "_R"
        else:
            suffix = ""
        
        # Increment the corresponding counter
        counters[suffix] += 1
        
        # Name the locator with the "Arm_" or "Leg_" prefix before "IK_" or "FK_", and number and suffix
        locator_name = f"{prefix}{locator_prefix}_gazelle{counters[suffix]}_loc{suffix}"
        
        # Create the locator
        locator = cmds.spaceLocator(name=locator_name)[0]
        
        # Perform a Match Transform (position, rotation, and scale)
        cmds.matchTransform(locator, selected_object, position=True, rotation=True, scale=True)
        
        # Add a parentConstraint to make the object control the locator
        cmds.parentConstraint(selected_object, locator, maintainOffset=False)
        
        # Display a message for each locator created
        print(f"Locator '{locator_name}' created, aligned with '{selected_object}', and constrained with parentConstraint.")

# Execute the function
create_group_based_on_selection()
