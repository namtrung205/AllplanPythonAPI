<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Begin\CreatePythonPart\CreatePipePythonPart.py</Name>
        <Title>Pipe Python Part</Title>
        <ReadLastInput>True</ReadLastInput>
        <Version>1.0</Version>
    </Script>
    <Page>
        <Name>Page1</Name>
        <Text>Pipe</Text>

        <Parameter>
            <Name>Length</Name>
            <Text>Length</Text>
            <Value>1000.</Value>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>Diameter</Name>
            <Text>Diameter</Text>
            <Value>100.</Value>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>Thickness</Name>
            <Text>Thickness</Text>
            <Value>3.</Value>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>IncludePad</Name>
            <Text>Include Pad</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>PadDiameter</Name>
            <Text>Pad Diameter</Text>
            <Value>150.</Value>
            <Visible>IncludePad == True</Visible>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>PadThickness</Name>
            <Text>Pad Thickness</Text>
            <Value>3.</Value>
            <Visible>IncludePad == True</Visible>
            <ValueType>Length</ValueType>
        </Parameter>
    </Page>
</Element>