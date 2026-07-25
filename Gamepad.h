#pragma once
#include <Windows.h>
#include <Xinput.h>
#pragma comment(lib, "XInput.lib")
#define GP_A        0
#define GP_B        1
#define GP_X        2
#define GP_Y        3
#define GP_LB       4
#define GP_RB       5
#define GP_LTHUMB   6
#define GP_RTHUMB   7
#define GP_START    8
#define GP_BACK     9
#define GP_DPAD_UP      10
#define GP_DPAD_DOWN    11
#define GP_DPAD_LEFT    12
#define GP_DPAD_RIGHT   13
#define GP_NUM_BUTTONS  14
class MHGamepad
{
public:
    static bool Initialize();
    static void Update();
    static void Shutdown();
    static bool IsConnected(DWORD userIndex);
    static void SetEnabled(bool en);
    static bool IsEnabled();
    static const DWORD* GetXInputButtons();
private:
    static bool enabled;
    static DWORD prevButtons[4];
    static int deadzoneX;
    static int deadzoneY;
    static int sensitivity;
    static void HandleGamepad(DWORD userIndex, XINPUT_STATE* state);
    static void SimulateMouseMove(short stickX, short stickY);
    static void HandleButton(DWORD userIndex, WORD xinputButton, bool pressed, WORD actionScancode);
};