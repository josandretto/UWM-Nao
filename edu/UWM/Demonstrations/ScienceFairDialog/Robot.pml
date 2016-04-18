<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Robot" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="ExampleDialog" src="behavior_1/ExampleDialog/ExampleDialog.dlg" />
        <Dialog name="School" src="School/School.dlg" />
    </Dialogs>
    <Resources>
        <File name="example" src="example" />
    </Resources>
    <Topics>
        <Topic name="ExampleDialog_enu" src="behavior_1/ExampleDialog/ExampleDialog_enu.top" topicName="ExampleDialog" language="en_US" />
        <Topic name="School_enu" src="School/School_enu.top" topicName="School" language="en_US" />
    </Topics>
    <IgnoredPaths />
</Package>
