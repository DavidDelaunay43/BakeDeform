import maya.cmds as cmds
from maya import cmds


def transfer_deformation_to_blendshape(
    base_geo: str, deformed_geo: str, blendshape_node: str, controlers: dict
):
    """
    controlers = {
        "ctrl_lattice_eye_L": {
            "tx": [-0.5, 0.5],
            "ty": [-0.5, 0.5],
            "tz": [-0.5, 0.5]
        },
        "ctrl_lattice_eye_R": {
            "tx": [-0.5, 0.5],
            "ty": [-0.5, 0.5],
            "tz": [-0.5, 0.5]
        }
    }
    """

    def transfer(
        base_geo: str,
        deformed_geo: str,
        blendshape_node: str,
        control: str,
        axis: str,
        value: float,
        suffix: str = "",
    ):
        """
        # mettre l'attribut du controleur à sa valeur
        # add target
        # renommer la target
        # créer le remap value et le connecter
        # reset l'attribut du controleur
        # incrémenter i
        """

        base_geo = cmds.listRelatives(base_geo, shapes=True)[0]
        deformed_geo = cmds.listRelatives(deformed_geo, shapes=True)[0]

        weight_num = cmds.listAttr(f"{blendshape_node}.w", multi=True)
        if not weight_num:
            index = 0
        else:
            index = len(weight_num)

        cmds.setAttr(f"{control}.{axis}", value)
        print(base_geo, index, deformed_geo)
        cmds.blendShape(
            blendshape_node,
            edit=True,
            topologyCheck=True,
            target=[base_geo, index, deformed_geo, 1.0],
            weight=[index, 0.0],
            tangentSpace=True,
        )
        cmds.aliasAttr(f"{control}_{axis}{suffix}", f"{blendshape_node}.w[{index}]")

        bad_attribute = cmds.listConnections(
            f"{deformed_geo}.worldMesh[0]", source=False, destination=True, plugs=True
        )
        if bad_attribute:
            cmds.disconnectAttr(f"{deformed_geo}.worldMesh[0]", bad_attribute[0])

        if axis.startswith("s"):
            cmds.setAttr(f"{control}.{axis}", 1)
        else:
            cmds.setAttr(f"{control}.{axis}", 0)

        rm_node = cmds.createNode("remapValue", name=f"rm_{control}_{axis}{suffix}")
        if axis.startswith("s"):
            cmds.setAttr(f"{rm_node}.inputMin", 1)
        cmds.setAttr(f"{rm_node}.inputMax", value)
        cmds.connectAttr(f"{control}.{axis}", f"{rm_node}.inputValue")
        cmds.connectAttr(
            f"{rm_node}.outValue",
            f"{blendshape_node}.{control}_{axis}{suffix}",
            force=True,
        )

    for control, transforms in controlers.items():

        for axis, values in transforms.items():

            if len(values) == 2:
                v_min, v_max = values
                transfer(
                    base_geo,
                    deformed_geo,
                    blendshape_node,
                    control,
                    axis,
                    v_min,
                    suffix="_min",
                )
                transfer(
                    base_geo,
                    deformed_geo,
                    blendshape_node,
                    control,
                    axis,
                    v_max,
                    suffix="_max",
                )

            else:
                value = values[0]
                transfer(base_geo, deformed_geo, blendshape_node, control, axis, value)
