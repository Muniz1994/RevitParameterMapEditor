import streamlit as st

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="expanded",

)

def parse_property_sets(file_content):
    """
    Parses the content of the ThesisParameterSets.V2.txt file
    into a dictionary structure.
    """
    property_sets = []
    current_pset = None
    for line in file_content.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("PropertySet:"):
            if current_pset:
                property_sets.append(current_pset)
            parts = line.replace("PropertySet:", "").strip().split('\t')
            name = parts[0]
            pset_type = parts[1]
            ifc_classes = parts[2].split(',')
            current_pset = {
                "name": name,
                "type": pset_type,
                "ifc_classes": [cls.strip() for cls in ifc_classes],
                "properties": []
            }
        elif current_pset:
            parts = line.split('\t')
            if len(parts) == 3:
                prop_name_ifc = parts[0]
                prop_type = parts[1]
                prop_name_revit = parts[2]
                current_pset["properties"].append({
                    "name_ifc": prop_name_ifc,
                    "type": prop_type,
                    "name_revit": prop_name_revit
                })
    if current_pset:
        property_sets.append(current_pset)
    return property_sets

def format_property_sets_for_saving(property_sets):
    """
    Formats the property set data back into the original file format.
    """
    output_lines = []
    for pset in property_sets:
        output_lines.append(f"PropertySet:\t{pset['name']}\t{pset['type']}\t{','.join(pset['ifc_classes'])}")
        for prop in pset['properties']:
            output_lines.append(f"\t{prop['name_ifc']}\t{prop['type']}\t{prop['name_revit']}")
    return "\n".join(output_lines)

def app():
    st.title("Revit Parameter mapping table Editor V0.1", help="Edit and manage your Revit parameter mapping tables easily.")

    st.link_button("🔎 Go to Revit-IFC manual reference", "https://autodesk.ifc-manual.com/revit/ifc-export-settings-dialog/property-sets/parameter-mapping-table", type="tertiary")

    uploaded_file = st.sidebar.file_uploader("Upload your Mapping table txt file", type=["txt"])

    # Only process the uploaded file when a new file is added (not on every rerun)
    if uploaded_file is not None:
        if "last_uploaded_file_name" not in st.session_state or uploaded_file.name != st.session_state["last_uploaded_file_name"]:
            file_content = uploaded_file.read().decode("utf-8")
            st.session_state.property_sets = parse_property_sets(file_content)
            st.session_state["last_uploaded_file_name"] = uploaded_file.name
            st.sidebar.success("File loaded successfully!")
            # Reset input fields for new Pset/Property after file upload
            st.session_state["new_pset_name_input"] = ""
            st.session_state["new_pset_ifc_classes_input"] = ""

    elif 'property_sets' not in st.session_state:
        # If no file is uploaded yet, and it's the first run, initialize with empty data
        st.session_state.property_sets = []
        st.info("Please upload a .txt file to get started or add new property sets.")

    # Initialize session state for new property set inputs if they don't exist
    if "new_pset_name_input" not in st.session_state:
        st.session_state["new_pset_name_input"] = ""
    if "new_pset_type_select" not in st.session_state:
        st.session_state["new_pset_type_select"] = "I"
    if "new_pset_ifc_classes_input" not in st.session_state:
        st.session_state["new_pset_ifc_classes_input"] = ""

    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                width: 400px !important; # Set the width to your desired value
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.subheader("Add New Property Set")
        new_property_set_name = st.text_input(
            "New Property Set Name",
            value=st.session_state["new_pset_name_input"],
            key="new_pset_name_input_widget"
        )
        new_property_set_type = st.selectbox(
            "New Property Set Type",
            ["I", "T"],
            index=["I", "T"].index(st.session_state["new_pset_type_select"]),
            key="new_pset_type_select_widget",
            help="Select 'I' for Instance Property Sets or 'T' for Type Property Sets"
        )
        new_property_set_ifc_classes = st.text_input(
            "New Property Set IFC Classes (comma-separated)",
            value=st.session_state["new_pset_ifc_classes_input"],
            key="new_pset_ifc_classes_input_widget"
        )

        if st.button("Add New Property Set to List"):
            if new_property_set_name and new_property_set_ifc_classes:
                st.session_state.property_sets.append({
                    "name": new_property_set_name,
                    "type": new_property_set_type,
                    "ifc_classes": [cls.strip() for cls in new_property_set_ifc_classes.split(',')],
                    "properties": []
                })
                st.success(f"Added new Property Set: {new_property_set_name}")
                # Clear the input fields after adding
                st.session_state["new_pset_name_input"] = ""
                st.session_state["new_pset_type_select"] = "I"
                st.session_state["new_pset_ifc_classes_input"] = ""
                st.rerun()  # Rerun to reflect changes and clear inputs
            else:
                st.warning("Please provide a name and IFC classes for the new Property Set.")
    
        st.markdown("---")

        # Add a download button at the end of the sidebar
        if 'property_sets' in st.session_state and st.session_state.property_sets:
            sidebar_edited_content = format_property_sets_for_saving(st.session_state.property_sets)
            st.download_button(
                type="primary",
                label="Download Parameters Mapping Table File",
                data=sidebar_edited_content,
                file_name="ThesisParameterSets_edited.txt",
                mime="text/plain",
                key="sidebar_download_button"
            )


    if 'property_sets' in st.session_state and st.session_state.property_sets:
        for i, pset in enumerate(st.session_state.property_sets):
            with st.expander(f"Property Set: {pset['name']} [{"Instance" if pset['type'] == "I" else "Type"}]", expanded=False):
                # Editable general information for existing Psets
                col1, col2, col3 = st.columns(3)
                with col1:
                    pset['name'] = st.text_input("Name", pset['name'], key=f"pset_name_{i}")
                with col2:
                    pset['type'] = st.selectbox("Type", ["I", "T"], index=["I", "T"].index(pset['type']), key=f"pset_type_{i}", help="Select 'I' for Instance Property Sets or 'T' for Type Property Sets")
                with col3:
                    ifc_classes_str = st.text_input("Applicable IFC Classes", ", ".join(pset['ifc_classes']), key=f"pset_ifc_classes_{i}")
                    pset['ifc_classes'] = [cls.strip() for cls in ifc_classes_str.split(',')]

                st.markdown("**Properties:**")
                for j, prop in enumerate(pset['properties']):
                    col1_prop, col2_prop, col3_prop, col4_prop = st.columns([1, 1, 1, 0.2]) # Added a column for the remove button
                    with col1_prop:
                        prop['name_ifc'] = st.text_input("IFC Name", prop['name_ifc'], key=f"prop_name_ifc_{i}_{j}")
                    with col2_prop:
                        type_options = [
                            "Acceleration", "AngularVelocity", "Area", "AreaDensity", "Boolean", "ClassificationReference", "ColorTemperature", "Count", "Currency", "DynamicViscosity", "ElectricCurrent", "ElectricVoltage", "Energy", "ElectricalEfficacy", "Force", "Frequency", "HeatFluxDensity", "HeatingValue", "Identifier", "Illuminance", "Integer", "IonConcentration", "IsothermalMoistureCapacity", "Label", "Length", "LinearForce", "LinearMoment", "LinearStiffness", "LinearVelocity", "Logical", "LuminousFlux", "LuminousIntensity", "Mass", "MassDensity", "MassFlowRate", "MassPerLength", "ModulusOfElasticity", "MoistureDiffusivity", "MomentOfInertia", "NormalisedRatio", "Numeric", "PlanarForce", "PlaneAngle", "PositiveLength", "PositivePlaneAngle", "PositiveRatio", "Power", "Pressure", "Ratio", "Real", "RotationalFrequency", "SoundPower", "SoundPressure", "SpecificHeatCapacity", "Text", "ThermalConductivity", "ThermalExpansionCoefficient", "ThermalResistance", "ThermalTransmittance", "ThermodynamicTemperature", "Time", "Torque", "VaporPermeability", "Volume", "VolumetricFlowRate", "WarpingConstant"
                        ]
                        # Default to first option if current value not in list
                        current_type = prop['type'] if prop['type'] in type_options else type_options[0]
                        prop['type'] = st.selectbox(
                            "Type", type_options, index=type_options.index(current_type), key=f"prop_type_{i}_{j}"
                        )
                    with col3_prop:
                        prop['name_revit'] = st.text_input("Revit Name", prop['name_revit'], key=f"prop_name_revit_{i}_{j}")
                    with col4_prop:
                        st.markdown("<br>", unsafe_allow_html=True) # Add some space
                        if st.button("X", key=f"remove_prop_{i}_{j}", help="Remove this property"):
                            st.session_state.property_sets[i]['properties'].pop(j)
                            st.rerun()

                st.markdown("---")

                # Inputs for adding new properties to *this specific* property set
                st.write(f"**Add new property to {pset['name']}:**")

                # Initialize session state for new property inputs if they don't exist
                if f"new_prop_name_ifc_{i}" not in st.session_state:
                    st.session_state[f"new_prop_name_ifc_{i}"] = ""
                if f"new_prop_type_{i}" not in st.session_state:
                    st.session_state[f"new_prop_type_{i}"] = ""
                if f"new_prop_name_revit_{i}" not in st.session_state:
                    st.session_state[f"new_prop_name_revit_{i}"] = ""

                new_prop_name_ifc = st.text_input("IFC Name", value=st.session_state[f"new_prop_name_ifc_{i}"], key=f"new_prop_name_ifc_widget_{i}")
                type_options = [
                    "Acceleration", "AngularVelocity", "Area", "AreaDensity", "Boolean", "ClassificationReference", "ColorTemperature", "Count", "Currency", "DynamicViscosity", "ElectricCurrent", "ElectricVoltage", "Energy", "ElectricalEfficacy", "Force", "Frequency", "HeatFluxDensity", "HeatingValue", "Identifier", "Illuminance", "Integer", "IonConcentration", "IsothermalMoistureCapacity", "Label", "Length", "LinearForce", "LinearMoment", "LinearStiffness", "LinearVelocity", "Logical", "LuminousFlux", "LuminousIntensity", "Mass", "MassDensity", "MassFlowRate", "MassPerLength", "ModulusOfElasticity", "MoistureDiffusivity", "MomentOfInertia", "NormalisedRatio", "Numeric", "PlanarForce", "PlaneAngle", "PositiveLength", "PositivePlaneAngle", "PositiveRatio", "Power", "Pressure", "Ratio", "Real", "RotationalFrequency", "SoundPower", "SoundPressure", "SpecificHeatCapacity", "Text", "ThermalConductivity", "ThermalExpansionCoefficient", "ThermalResistance", "ThermalTransmittance", "ThermodynamicTemperature", "Time", "Torque", "VaporPermeability", "Volume", "VolumetricFlowRate", "WarpingConstant"
                ]
                current_type = st.session_state[f"new_prop_type_{i}"] if st.session_state[f"new_prop_type_{i}"] in type_options else type_options[0]
                new_prop_type = st.selectbox(
                    "Type",
                    type_options,
                    index=type_options.index(current_type),
                    key=f"new_prop_type_widget_{i}"
                )
                new_prop_name_revit = st.text_input("Revit Name", value=st.session_state[f"new_prop_name_revit_{i}"], key=f"new_prop_name_revit_widget_{i}")

                if st.button(f"Add Property to {pset['name']}", key=f"add_prop_to_pset_button_{i}"):
                    if new_prop_name_ifc and new_prop_type and new_prop_name_revit:
                        st.session_state.property_sets[i]['properties'].append({
                            "name_ifc": new_prop_name_ifc,
                            "type": new_prop_type,
                            "name_revit": new_prop_name_revit
                        })
                        st.success(f"Added new property to {pset['name']}")
                        # Clear the input fields after adding
                        st.session_state[f"new_prop_name_ifc_{i}"] = ""
                        st.session_state[f"new_prop_type_{i}"] = ""
                        st.session_state[f"new_prop_name_revit_{i}"] = ""
                        st.rerun() # Rerun to reflect changes and clear inputs
                    else:
                        st.warning("Please fill all fields for the new property.")
                st.markdown("---")

                if st.button(f"Remove Property Set: {pset['name']}", key=f"remove_pset_{i}", type="primary", help="Remove this property set"):
                    st.session_state.property_sets.pop(i)
                    st.rerun()

    else:
        st.warning("No property sets loaded. Upload a file or use the sidebar to add a new property set.")

if __name__ == "__main__":
    app()