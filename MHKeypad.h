// четыре клавиши, которые может нажимать. Возможно, две соседние
#ifndef __MH_KEYPAD
#define __MH_KEYPAD
class MHKeypad
{
public:
	static void Init(const WORD (&scancodes)[17]);
	static void Reset(int shift=0);
	static int GetPosition(){return keypad_position;};
	static void Press(int position, bool down, int shift=0);
	//static void Press4(int position, bool down, int shift=0);
	static bool Press4(int position, bool down, int shift=0); // теперь возвращает false если реального нажатия не было - это для правой кнопки мыни надо было
	static void Press8(int position, bool down); // Для 8 умений
protected:
	static int keypad_position;
	static WORD scancode[17];
};
#endif