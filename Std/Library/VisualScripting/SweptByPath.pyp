<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>NodeScript.py</Name>
        <Title>NodeScript</Title>
        <Version>1.0</Version>
        <Interactor>True</Interactor>
        <ReadLastInput>True</ReadLastInput>
        <SubElements>SweptByPath.pyp</SubElements>
    </Script>
    <SubElement>
        <PyP>Etc\VisualScripts\Geometry\CurvesInput\NodeCircle3DInput.pypsub</PyP>
        <PageIndex>0</PageIndex>
        <Name>Circle3DInput</Name>
        <ID>Circle3DInput</ID>
        <Position>2369,1714</Position>
        <DefaultValues>
            <CreateModelPreviewObjects>
                <Value>True</Value>
            </CreateModelPreviewObjects>
        </DefaultValues>
    </SubElement>
    <SubElement>
        <PyP>Etc\VisualScripts\Geometry\Objects\NodeExtrudeAlongVector.pypsub</PyP>
        <PageIndex>0</PageIndex>
        <Name>ExtrudeAlongVector</Name>
        <ID>ExtrudeAlongVector</ID>
        <Position>2661,1689</Position>
        <DefaultValues>
            <ExtrusionVector>
                <Value>Vector3D(0, 0, 1000)</Value>
            </ExtrusionVector>
            <ExtrudeFromCenter>
                <Value>True</Value>
            </ExtrudeFromCenter>
            <CreateModelObjects>
                <Value>True</Value>
            </CreateModelObjects>
            <CreateModelPreviewObjects>
                <Value>True</Value>
            </CreateModelPreviewObjects>
        </DefaultValues>
        <Constraints>
            <ObjectToExtrude>
                <Value>Circle3DInput:Circle</Value>
                <Visible>False</Visible>
            </ObjectToExtrude>
        </Constraints>
    </SubElement>
</Element>