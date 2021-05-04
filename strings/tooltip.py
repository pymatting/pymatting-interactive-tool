# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

brushToolTip = (
    "(B)rush -\n"
    "Left-Click and Drag: Draw inside the trimap in the left view\n"
    "Shift+WheelUp/Shift+WheelDown or +/-: Increase/Decrease brush width\n"
    "1/2/3/4: Changes color to green(foreground)/red(background)/blue(unknown)/transparent(unknown)"
)

paintBucketToolTip = (
    "(P)aintbucket -\n"
    "Left-Click: Fill trimap area based on canvas\n"
    "Ctrl+Left-Click: Fill trimap area based on trimap\n"
    "Shift+WheelUp/Shift+WheelDown or +/-: Increase/Decrease threshold value\n"
    "1/2/3/4: Changes color to green(foreground)/red(background)/blue(unknown)/transparent(unknown)"
)

cropToolTip = (
    "(C)rop - \n" "Left-Click and Drag: Select crop region\n" "Right-Click: Cancel"
)

scaleToolTip = (
    "(S)cale - \n" "Opens up a Dialog where the Project can be scaled up or down."
)


dragToolTip = (
    "(D)rag - \n"
    "Press and move the left mouse button to pan around in both views.\n"
    "Pressing spacebar activates dragging, releasing the spacebar deactivates dragging."
)

clearTrimapToolTip = "Clear the Trimap."

clearNewBackgroundToolTip = "Remove the new Background."

startToolTip = "Start/Continue the calculations"

pauseToolTip = "Pause the calculations."

stopToolTip = (
    "Stop the calculations.\nWarning: Pressing stop will reset the alpha matte."
)

fileTreeToolTip = "Show/Hide the File Explorer"

colorBleedToolTip = "Checking this button will reduce color bleeding when saving."

cutoutPreviewToolTip = "(R)ealtime Cutout Preview - This button disables/enables the realtime cutout preview."

paintBucketValueToolTip = "Adjust the paintbuckets 'strength'. The higher the value, the stronger the paintbucket."

brushWidthSliderToolTip = "Drag the slider to increase/decrease the brush width. \nAlternatively: Shift + Scroll or +/- on the keyboard."

colorPushButtonToolTip = "Pressing this button cycles through all possible colors"

laplacianToolTip = "Laplacian that is being used"

radiusToolTip = "<html><head/><body><p>Set the radius of the local window size. </p><p>Default: 1</p></body></html>"

epsilonToolTip = "<html><head/><body><p>Set the regularization strength. </p><p>Default: 0,0000001</p></body></html>"

methodToolTip = "<html><head/><body><p>Set the method of the Solver.</p><p>Default: cgd (Conjugate Gradient Descent)</p></body></html>"

preconditionerToolTip = "<html><head/><body><p>Set the preconditioner for cgd.</p><p>Default: none</p></body></html>"

kernelToolTip = "<html><head/><body><p>Set the kernel for the V-Cycle solver.</p><p>Default: gaussian</p></body></html>"

toleranceToolTip = "<html><head/><body><p>Set the tolerance value. Calculations will stop automatically, if the error falls below this value. All values get converted to 1e-tolerance except zero, which stands for &quot;disabled&quot; i.e. calculations never stop.</p><p>Default: disabled </p></body></html>"

lambdaToolTip = (
    "<html><head/><body><p>Constraint penalty</p><p>Default: 100</p></body></html>"
)

preIterToolTip = "<html><head/><body><p>Number of smoothing iterations before each V-Cycle</p><p>Default: 1</p></body></html>"

postIterToolTip = "<html><head/><body><p>Number of smoothing iterations after each V-Cycle</p><p>Default: 1</p></body></html>"

increaseSmoothnessToolTip = "Increase Alpha Smoothness"

decreaseSmoothnessToolTip = "Decrease Alpha Smoothness"
