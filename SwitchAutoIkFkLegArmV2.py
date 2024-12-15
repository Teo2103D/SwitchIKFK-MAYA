import maya.cmds as cmds
import re

# Function to remove namespaces
def remove_namespace(locator_name):
    if ':' in locator_name:
        # Removes everything before the first ':' (namespace)
        return locator_name.split(':')[-1]
    return locator_name

# Function to perform the search and matching of locators
def match_transforms_to_locators(selected_group):
    # Retrieve selected objects
    selected_objects = cmds.ls(selection=True)

    if len(selected_objects) == 0:
        cmds.error("Please select at least one object.")
        return

    # Determine the category (arm or leg) of the selection
    category = determine_category(selected_objects)

    # Apply rules based on the number of selected objects
    if len(selected_objects) in [3, 6]:
        match_to_fk_locators(selected_objects, category, selected_group)
    elif len(selected_objects) in [2, 4]:
        match_to_ik_locators(selected_objects, category, selected_group)
    else:
        cmds.error(f"The script only works with 2, 4, 3, or 6 selected objects. You have selected {len(selected_objects)} objects.")

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
            # Do not replace the "Arm" and "Leg" prefixes, but use only the selected name
            if category == "arm":
                locator_name = f"Arm_FK_{selected_group}{i+1}_loc{suffix}"
            elif category == "leg":
                locator_name = f"Leg_FK_{selected_group}{i+1}_loc{suffix}"
            else:
                locator_name = f"{selected_group}_FK_{selected_group}{i+1}_loc{suffix}"

            # Remove namespace from the locator name
            locator_name = remove_namespace(locator_name)

            # Get all locators in the scene with namespaces
            all_locators = cmds.ls(type="locator", long=True)

            # Compare the name without namespace and look for a partial match
            for full_locator_name in all_locators:
                if locator_name in remove_namespace(full_locator_name):  # Check if the searched name is part of the full name
                    locators.append(full_locator_name)
                    break
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
                if current_suffix == '_L':
                    locator_name = f"Arm_IK_PV_{selected_group}_loc_L"
                elif current_suffix == '_R':
                    locator_name = f"Arm_IK_PV_{selected_group}_loc_R"
                else:
                    locator_name = f"Arm_IK_PV_{selected_group}_loc"
            elif category == "leg":
                if current_suffix == '_L':
                    locator_name = f"Leg_IK_PV_{selected_group}_loc_L"
                elif current_suffix == '_R':
                    locator_name = f"Leg_IK_PV_{selected_group}_loc_R"
                else:
                    locator_name = f"Leg_IK_PV_{selected_group}_loc"
            else:
                locator_name = f"{selected_group}_IK_PV_{selected_group}_loc"
        else:
            if category == "arm":
                if current_suffix == '_L':
                    locator_name = f"Arm_IK_{selected_group}1_loc_L"
                elif current_suffix == '_R':
                    locator_name = f"Arm_IK_{selected_group}1_loc_R"
                else:
                    locator_name = f"Arm_IK_{selected_group}1_loc"
            elif category == "leg":
                if current_suffix == '_L':
                    locator_name = f"Leg_IK_{selected_group}1_loc_L"
                elif current_suffix == '_R':
                    locator_name = f"Leg_IK_{selected_group}1_loc_R"
                else:
                    locator_name = f"Leg_IK_{selected_group}1_loc"
            else:
                locator_name = f"{selected_group}_IK_{selected_group}1_loc"

        # Remove namespace from the locator name
        locator_name = remove_namespace(locator_name)

        # Get all locators in the scene with namespaces
        all_locators = cmds.ls(type="locator", long=True)

        # Compare the name without namespace and look for a partial match
        for full_locator_name in all_locators:
            if locator_name in remove_namespace(full_locator_name):  # Check if the searched name is part of the full name
                # Perform MAT with the found locator
                cmds.matchTransform(obj, full_locator_name, position=True, rotation=True, scale=False)
                print(f"MAT performed: {obj} -> {full_locator_name}")
                break
        else:
            cmds.warning(f"The locator {locator_name} does not exist for object {obj}.")

        last_suffix = current_suffix

# Execute the detection of unique locators and matching of transforms
detect_unique_locator_names()
