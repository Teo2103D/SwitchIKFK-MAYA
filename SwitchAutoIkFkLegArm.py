import maya.cmds as cmds

def match_transforms_to_locators():
    # Retrieve the selection
    selected_objects = cmds.ls(selection=True)
    
    # Check if there are selected objects
    if len(selected_objects) == 0:
        cmds.error("Please select at least one object.")
        return

    # Determine the category (arm or leg) of the selection
    category = determine_category(selected_objects)
    
    # Apply rules based on the number of selected objects
    if len(selected_objects) in [3, 6]:
        # Apply the rules of the first script with category distinction
        match_to_fk_locators(selected_objects, category)
    elif len(selected_objects) in [2, 4]:
        # Apply the rules of the second script with category distinction
        match_to_ik_locators(selected_objects, category)
    else:
        cmds.error(f"The script only works with 2, 4, 3, or 6 selected objects. You have selected {len(selected_objects)} objects.")

def determine_category(selected_objects):
    arm_list = ["wrist", "hand", "elbow", "arm", "shoulder", "clavicle", "poignet", "main", "coude", "bras", "epaule", "clavicule"]
    leg_list = ["hip", "pelvis", "femur", "kneecap", "knee", "leg", "ankle", "foot", "tibia", "hanche", "bassin", "rotule", "genou", "cheville", "pied", "waist", "hinge", "heel", "toe"]

    is_arm = any(any(word.lower() in obj.lower() for word in arm_list) for obj in selected_objects)
    is_leg = any(any(word.lower() in obj.lower() for word in leg_list) for obj in selected_objects)

    if is_arm and is_leg:
        cmds.error("The selection contains objects from both the 'arm' and 'leg' groups.")
        return None
    elif is_arm:
        return "arm"
    elif is_leg:
        return "leg"
    else:
        cmds.error("The selection does not match any valid group ('arm' or 'leg').")
        return None

def match_to_fk_locators(selected_objects, category):
    """Rules for FK locators (3 or 6 objects)"""
    def get_suffix(obj_name):
        if obj_name.endswith('_L'):
            return '_L'
        elif obj_name.endswith('_R'):
            return '_R'
        else:
            return ''

    # Separate the objects by suffix
    objects_L = [obj for obj in selected_objects if get_suffix(obj) == '_L']
    objects_R = [obj for obj in selected_objects if get_suffix(obj) == '_R']
    objects_none = [obj for obj in selected_objects if get_suffix(obj) == '']

    def get_locators(objects, suffix):
        locators = []
        for i, obj in enumerate(objects):
            # Fix: Use 'Arm_' or 'Leg_' prefixes depending on the category
            if category == "arm":
                locator_name = f"Arm_FK_gazelle{i+1}_loc{suffix}"
            elif category == "leg":
                locator_name = f"Leg_FK_gazelle{i+1}_loc{suffix}"
            else:
                locator_name = f"FK_gazelle{i+1}_loc{suffix}"
            if cmds.objExists(locator_name):
                locators.append(locator_name)
            else:
                cmds.warning(f"The locator {locator_name} does not exist.")
        return locators

    locators_L = get_locators(objects_L, '_L')
    locators_R = get_locators(objects_R, '_R')
    locators_none = get_locators(objects_none, '')

    for obj in selected_objects:
        suffix = get_suffix(obj)
        locator_to_match = None
        if suffix == '_L' and locators_L:
            locator_to_match = locators_L.pop(0)
        elif suffix == '_R' and locators_R:
            locator_to_match = locators_R.pop(0)
        elif suffix == '' and locators_none:
            locator_to_match = locators_none.pop(0)

        if locator_to_match:
            cmds.matchTransform(obj, locator_to_match, position=True, rotation=True, scale=False)
            print(f"MAT performed: {obj} -> {locator_to_match}")

def match_to_ik_locators(selected_objects, category):
    """Rules for IK locators (2 or 4 objects)"""
    def get_suffix(obj_name):
        if obj_name.endswith('_L'):
            return '_L'
        elif obj_name.endswith('_R'):
            return '_R'
        else:
            return ''

    suffix_counts = {"_L": 0, "_R": 0, "": 0}

    for obj in selected_objects:
        suffix = get_suffix(obj)
        suffix_counts[suffix] += 1
        if suffix_counts[suffix] > 2:
            cmds.error(f"You cannot select more than two objects with the suffix '{suffix}'.")

    last_suffix = None

    for obj in selected_objects:
        current_suffix = get_suffix(obj)
        
        if last_suffix is None or last_suffix != current_suffix:
            # Fix: Generate locators with 'Arm_' or 'Leg_' prefixes depending on the category
            if category == "arm":
                if current_suffix == '_L':
                    locator_name = "Arm_IK_PV_gazelle_loc_L"
                elif current_suffix == '_R':
                    locator_name = "Arm_IK_PV_gazelle_loc_R"
                else:
                    locator_name = "Arm_IK_PV_gazelle_loc"
            elif category == "leg":
                if current_suffix == '_L':
                    locator_name = "Leg_IK_PV_gazelle_loc_L"
                elif current_suffix == '_R':
                    locator_name = "Leg_IK_PV_gazelle_loc_R"
                else:
                    locator_name = "Leg_IK_PV_gazelle_loc"
            else:
                locator_name = "IK_PV_gazelle_loc"
        else:
            # Same logic, but for IK type locators (based on the category)
            if category == "arm":
                if current_suffix == '_L':
                    locator_name = "Arm_IK_gazelle1_loc_L"
                elif current_suffix == '_R':
                    locator_name = "Arm_IK_gazelle1_loc_R"
                else:
                    locator_name = "Arm_IK_gazelle1_loc"
            elif category == "leg":
                if current_suffix == '_L':
                    locator_name = "Leg_IK_gazelle1_loc_L"
                elif current_suffix == '_R':
                    locator_name = "Leg_IK_gazelle1_loc_R"
                else:
                    locator_name = "Leg_IK_gazelle1_loc"
            else:
                locator_name = "IK_gazelle1_loc"

        # Search for locators with the correct prefix for the category
        if cmds.objExists(locator_name):
            # Check the locator's position before applying
            locator_position = cmds.xform(locator_name, q=True, t=True, ws=True)
            if locator_position != [0.0, 0.0, 0.0]:  # If the locator is properly placed
                cmds.matchTransform(obj, locator_name, position=True, rotation=True, scale=False)
                print(f"MAT performed: {obj} -> {locator_name}")
            else:
                cmds.warning(f"The locator {locator_name} is mispositioned or missing in the scene.")
        else:
            cmds.warning(f"The locator {locator_name} does not exist for object {obj}.")

        last_suffix = current_suffix

# Execute the function
match_transforms_to_locators()
