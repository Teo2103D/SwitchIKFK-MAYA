import maya.cmds as cmds
import re

#By Teo MINANA

# Function to detect unique locator names and display a window
def detect_unique_locator_names():
    locators = cmds.ls(type="locator")

    if not locators:
        cmds.error("No locators found in the scene.")

    unique_names = set()
    name_pattern = re.compile(r"(?:Arm|Leg)_(?:FK|IK_PV)_([A-Za-z]+)\d*_loc_[LR]")

    for locator in locators:
        match = name_pattern.search(locator)
        if match:
            name = match.group(1)
            unique_names.add(name)

    if not unique_names:
        cmds.error("No valid names found in the locators.")
        return

    window_name = "locatorNamesWindow"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="Unique Locator Names", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Names found in locators:")
    locator_list = cmds.textScrollList(allowMultiSelection=False, height=150)

    for name in unique_names:
        cmds.textScrollList(locator_list, edit=True, append=name)

    cmds.button(label="Select Group", command=lambda x: apply_group_selection(locator_list))
    cmds.showWindow(window_name)

# Function to apply the selection of a locator group
def apply_group_selection(locator_list):
    selected_group = cmds.textScrollList(locator_list, q=True, selectItem=True)

    if not selected_group:
        cmds.error("Please select a locator group.")
        return

    selected_group = selected_group[0]
    match_transforms_to_locators(selected_group)

# Function to remove namespaces
def remove_namespace(locator_name):
    if ':' in locator_name:
        return locator_name.split(':')[-1]
    return locator_name

# Function to find an object even with a namespace
def find_object_with_partial_name(target_name):
    # List all objects
    all_objects = cmds.ls(long=True)

    # Search for objects containing the `target_name`
    for obj in all_objects:
        if target_name in obj:
            return obj  # Return the first matching object

    return None  # Return None if no object is found

# Function to detect the category (arm or leg) of selected objects
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

# Function to match transforms to FK locators
def match_to_fk_locators(selected_objects, category, selected_group):
    def get_suffix(obj_name):
        if obj_name.endswith('_L'):
            return '_L'
        elif obj_name.endswith('_R'):
            return '_R'
        else:
            return ''

    objects_L = [obj for obj in selected_objects if get_suffix(obj) == '_L']
    objects_R = [obj for obj in selected_objects if get_suffix(obj) == '_R']
    objects_none = [obj for obj in selected_objects if get_suffix(obj) == '']

    def get_locators(objects, suffix):
        locators = []
        for i, obj in enumerate(objects):
            if category == "arm":
                locator_name = f"Arm_FK_{selected_group}{i+1}_loc{suffix}"
            elif category == "leg":
                locator_name = f"Leg_FK_{selected_group}{i+1}_loc{suffix}"
            else:
                locator_name = f"{selected_group}_FK_{selected_group}{i+1}_loc{suffix}"

            # Find the object, handling namespaces
            full_locator_name = find_object_with_partial_name(locator_name)

            if full_locator_name:
                locators.append(full_locator_name)
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

# Function to match transforms to IK locators
def match_to_ik_locators(selected_objects, category, selected_group):
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
            if category == "arm":
                locator_name = f"Arm_IK_PV_{selected_group}_loc{current_suffix}"
            elif category == "leg":
                locator_name = f"Leg_IK_PV_{selected_group}_loc{current_suffix}"
            else:
                locator_name = f"{selected_group}_IK_PV_{selected_group}_loc{current_suffix}"
        else:
            if category == "arm":
                locator_name = f"Arm_IK_{selected_group}1_loc{current_suffix}"
            elif category == "leg":
                locator_name = f"Leg_IK_{selected_group}1_loc{current_suffix}"
            else:
                locator_name = f"{selected_group}_IK_{selected_group}1_loc{current_suffix}"

        full_locator_name = find_object_with_partial_name(locator_name)

        if full_locator_name:
            cmds.matchTransform(obj, full_locator_name, position=True, rotation=True, scale=False)
            print(f"MAT performed: {obj} -> {full_locator_name}")
        else:
            cmds.warning(f"The locator {locator_name} does not exist for object {obj}.")

        last_suffix = current_suffix

# Main function to match transforms to locators
def match_transforms_to_locators(selected_group):
    selected_objects = cmds.ls(selection=True)
    
    if len(selected_objects) == 0:
        cmds.error("Please select at least one object.")
        return

    category = determine_category(selected_objects)

    if len(selected_objects) in [3, 6]:
        match_to_fk_locators(selected_objects, category, selected_group)
    elif len(selected_objects) in [2, 4]:
        match_to_ik_locators(selected_objects, category, selected_group)
    else:
        cmds.error(f"The script only works with 2, 4, 3, or 6 selected objects. You have selected {len(selected_objects)} objects.")

# Execute the detection of unique locator names
detect_unique_locator_names()

#By Teo MINANA
