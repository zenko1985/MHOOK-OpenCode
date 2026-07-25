#include "Gamepad.h"
#include "Settings.h"
#include "Scancode.h"
bool MHGamepad::enabled = false;
DWORD MHGamepad::prevButtons[4] = {0};
int MHGamepad::deadzoneX = XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE;
int MHGamepad::deadzoneY = XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE;
int MHGamepad::sensitivity = 3;
static const DWORD gp_xinput_buttons[GP_NUM_BUTTONS] = {
	XINPUT_GAMEPAD_A, XINPUT_GAMEPAD_B, XINPUT_GAMEPAD_X, XINPUT_GAMEPAD_Y,
	XINPUT_GAMEPAD_LEFT_SHOULDER, XINPUT_GAMEPAD_RIGHT_SHOULDER,
	XINPUT_GAMEPAD_LEFT_THUMB, XINPUT_GAMEPAD_RIGHT_THUMB,
	XINPUT_GAMEPAD_START, XINPUT_GAMEPAD_BACK,
	XINPUT_GAMEPAD_DPAD_UP, XINPUT_GAMEPAD_DPAD_DOWN,
	XINPUT_GAMEPAD_DPAD_LEFT, XINPUT_GAMEPAD_DPAD_RIGHT
};
const DWORD* MHGamepad::GetXInputButtons()
{
	return gp_xinput_buttons;
}
bool MHGamepad::Initialize()
{
	if (!MHSettings::flag_gamepad_enabled) return false;
	sensitivity = MHSettings::gamepad_sensitivity;
	for (DWORD i = 0; i < 4; i++)
	{
		XINPUT_STATE state;
		if (XInputGetState(i, &state) == ERROR_SUCCESS)
		{
			enabled = true;
			return true;
		}
	}
	return false;
}
void MHGamepad::Update()
{
	if (!enabled) return;
	sensitivity = MHSettings::gamepad_sensitivity;
	for (DWORD i = 0; i < 4; i++)
	{
		XINPUT_STATE state;
		if (XInputGetState(i, &state) == ERROR_SUCCESS)
		{
			HandleGamepad(i, &state);
		}
	}
}
void MHGamepad::Shutdown()
{
	enabled = false;
}
bool MHGamepad::IsConnected(DWORD userIndex)
{
	if (userIndex >= 4) return false;
	XINPUT_STATE state;
	return XInputGetState(userIndex, &state) == ERROR_SUCCESS;
}
void MHGamepad::SetEnabled(bool en)
{
	enabled = en;
}
bool MHGamepad::IsEnabled()
{
	return enabled;
}
void MHGamepad::HandleGamepad(DWORD userIndex, XINPUT_STATE* state)
{
	short stickX = state->Gamepad.sThumbLX;
	short stickY = state->Gamepad.sThumbLY;
	if (stickX > deadzoneX || stickX < -deadzoneX ||
		stickY > deadzoneY || stickY < -deadzoneY)
	{
		SimulateMouseMove(stickX, stickY);
	}
	WORD buttons = state->Gamepad.wButtons;
	for (int i = 0; i < GP_NUM_BUTTONS; i++)
	{
		WORD action = MHSettings::gamepad_mapping[i];
		HandleButton(userIndex, gp_xinput_buttons[i], (buttons & gp_xinput_buttons[i]) != 0, action);
	}
	prevButtons[userIndex] = buttons;
}
void MHGamepad::SimulateMouseMove(short stickX, short stickY)
{
	double moveX = (stickX / 32767.0) * sensitivity;
	double moveY = (stickY / 32767.0) * sensitivity;
	INPUT input = {0};
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_MOVE;
	input.mi.dx = (LONG)moveX;
	input.mi.dy = (LONG)moveY;
	SendInput(1, &input, sizeof(INPUT));
}
static void SendMouseButton(DWORD downFlag, DWORD upFlag, bool pressed)
{
	INPUT input = {0};
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = pressed ? downFlag : upFlag;
	input.mi.dwExtraInfo = 0;
	input.mi.mouseData = 0;
	input.mi.time = 0;
	input.mi.dx = 0;
	input.mi.dy = 0;
	SendInput(1, &input, sizeof(INPUT));
}
static void SendScroll(short delta)
{
	INPUT input = {0};
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_WHEEL;
	input.mi.mouseData = delta;
	input.mi.dwExtraInfo = 0;
	input.mi.time = 0;
	input.mi.dx = 0;
	input.mi.dy = 0;
	SendInput(1, &input, sizeof(INPUT));
}
static void SendKeyboardKey(WORD scancode, bool pressed)
{
	INPUT input = {0};
	input.type = INPUT_KEYBOARD;
	input.ki.dwFlags = KEYEVENTF_SCANCODE;
	if (!pressed) input.ki.dwFlags |= KEYEVENTF_KEYUP;
	if (scancode > 0xFF)
		input.ki.dwFlags |= KEYEVENTF_EXTENDEDKEY;
	input.ki.wScan = scancode;
	SendInput(1, &input, sizeof(INPUT));
}
void MHGamepad::HandleButton(DWORD userIndex, WORD xinputButton, bool pressed, WORD actionScancode)
{
	bool wasPressed = (prevButtons[userIndex] & xinputButton) != 0;
	if (pressed && !wasPressed)
	{
		switch (actionScancode)
		{
		case SC_NONE:
			break;
		case SC_LMOUSE:
			SendMouseButton(MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, true);
			break;
		case SC_RMOUSE:
			SendMouseButton(MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP, true);
			break;
		case SC_MIDDLEMB:
			SendMouseButton(MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP, true);
			break;
		case SC_WHEEL_UP:
			SendScroll(WHEEL_DELTA);
			break;
		case SC_WHEEL_DOWN:
			SendScroll(-WHEEL_DELTA);
			break;
		default:
			SendKeyboardKey(actionScancode, true);
			break;
		}
	}
	else if (!pressed && wasPressed)
	{
		switch (actionScancode)
		{
		case SC_NONE:
		case SC_WHEEL_UP:
		case SC_WHEEL_DOWN:
			break;
		case SC_LMOUSE:
			SendMouseButton(MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, false);
			break;
		case SC_RMOUSE:
			SendMouseButton(MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP, false);
			break;
		case SC_MIDDLEMB:
			SendMouseButton(MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP, false);
			break;
		default:
			SendKeyboardKey(actionScancode, false);
			break;
		}
	}
}