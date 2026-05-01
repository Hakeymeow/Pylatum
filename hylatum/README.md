## Record of Sessions

- [**[/init-1]**](https://opncd.ai/share/MjX5DeGJ)
- [**[/init-2]**](https://opncd.ai/share/q2A70T6N)
- [**[/init-3]**](https://opncd.ai/share/vmATTxNu)

- [**[webview-qt]**](https://opncd.ai/share/BTdJ3FIB): I implemented the core McCabe-Thiele algorithm and decided to add a GUI with vibe coding. The agent added pywebview without [gtk] or [qt] extras to the dependencies, which may not work on Linux according to the official documentation, and manually added PyQt and other backend dependencies. The GUI took a long time to load — I thought (because the agent told me) it was due to the Qt backend's poor performance (but after the refactor I found the real culprit was waiting for the CDN).

- [**[webview-gtk]**](https://opncd.ai/share/AH5v4Pjk): There were other problems with the previous GUI. Its iteration visualization looked strange with two askew starting lines. The Qt backend dependencies were hard-coded in the source code, which prevented me from testing the GTK backend. It might be easier to build a new GUI, and I wanted a challenging task to see the advantage of the oh-my-openagent plugin.

- [**[pyinstaller]**](https://opncd.ai/share/lW3uFkxr): I tried building executables with PyInstaller at first but ran into a GTK issue. The Sisyphus agent tried its best and finally realized it is Sisyphus — and maybe realized it had become Sisyphus. The effort wasn't committed to the git repository, but the session is quite interesting.

- [**[nuitka]**](https://opncd.ai/share/wiQoPYCb): The Sisyphus agent recommended Nuitka before it gave up, so I switched. It did solve the GTK problem.

- [**[plot-R]**](https://opncd.ai/share/xwYH1QHK): I reviewed my tasks and found that I hadn't analyzed the correlation between $R$ and the plate number. I told the agent to do it, both to fill the gap and to add more vibe coding content to my report.

- [**[plotly]**](https://opncd.ai/share/yZcapNtP): `index.html` must contain `plotly.min.js` to render the plot correctly. It was originally imported via CDN, but I wanted the program to work offline. I noticed the agent had fetched a static `plotly.min.js` from the virtual environment, so I asked whether the program could do that on its own.

- [**[nuitka-venv]**](https://opncd.ai/share/zGEp5R2l): It struck me that I hadn't included plotly in `build.py`, yet the GUI program worked — so I assumed Nuitka was packaging the entire virtual environment. I removed manim and matplotlib and rebuilt the program. It still worked fine and the size did decrease. I then asked the agent to verify this and figure out what was going on.
