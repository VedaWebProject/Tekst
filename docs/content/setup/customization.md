# Customization


## Additional custom fonts

!!! info
    You **have to** set up [custom client assets](#custom-client-assets) as a preliminary step if you haven't done so already!

You can provide yourself and other users with the option to use alternative fonts for specific resources or on-screen keyboard modes. This can be useful when the content of a resource or an [OSK](#on-screen-keyboard) mode uses a specific character set or diacritics that cannot be displayed by the default font Tekst uses for contents.

To add additional fonts, you need access to the server on which the platform application is deployed!

1. Create a file `fonts.css` inside the directory you configured for [custom client assets](#custom-client-assets).
2. Create a folder `fonts` in the same directory. Here you can store your additional fonts (possibly sorted into further subfolders). It is recommended to prepare each font in different formats optimized for web use (see [here](https://developer.mozilla.org/en-US/docs/Learn/CSS/Styling_text/Web_fonts)!).
3. In the previously created `fonts.css`, create a complete `@font-face` definition for each of your fonts (again, see [here](https://developer.mozilla.org/en-US/docs/Learn/CSS/Styling_text/Web_fonts) for details). As the public path to the files, specify `/static/fonts/<...>`, replacing `<...>` with the path within your previously created `fonts` folder.
4. The value used for `font-family` in the `@font-face` definition can now be entered as an additional font in the platform's system settings. Pay attention to exact identical spelling!
5. The added fonts can now be selected as a different font in the settings for each text-based resource or in [OSK](#on-screen-keyboard) modes.

!!! tip
    Pay attention to the licensing of the fonts you use and, where applicable, include the corresponding license files with the font files.

!!! note "A note for advanced users"
    If you want to change the overall UI font or default resource font the client application uses, you might add your fonts following the steps above and then change the internal `@font-face` definitions in `Tekst-Web/public/fonts.css` (don't change the `font-family` names!). Use the public paths described above. Please note that for this change to take effect, you'll have to **re-build the client application**!


## On-screen keyboard

!!! info
    You **have to** set up [custom client assets](#custom-client-assets) as a preliminary step if you haven't done so already!

Tekst has an on-screen keyboard feature for easy input of special character sets in places where this might come in handy. Take the following steps to set up you custom on-screen keyboard character sets:

1. Create a folder `osk` inside the directory you configured for [custom client assets](#custom-client-assets).
2. For each OSK character set you want to provide, create a (valid!) `.json` file inside this `osk` folder following the format shown in the example below. For the name of your `.json` file, avoid using whitespaces or special characters. Keep it simple.
3. You can now set up available OSK modes (combinations of character maps and fonts used in the UI) in the administration settings of the client. Please use the exact name of the `.json` files you created (but without the `.json` extension!) as the `key` and a speaking `name` for each OSK mode.

!!! example
    Follow this format for your character sets' `.json` files. The outer array holds the lines of character groups that will be rendered in a common line on the on-screen keyboard (if possible). The inner arrays contain the groups of actual definitions of the keyboard's keys that will be rendered as groups of keys (somewhat closer to each other). For each character object, the `char` property is required. You can provide an optional `shift` property if you want the key on the keyboard to print an alternate character if the OSK's Shift key is toggled. Otherwise, `char` is used as a fallback.

    ```json
    [
        [
            [
                { "char": "a", "shift": "A" },
                { "char": "b", "shift": "B" }
            ],
            [
                { "char": "c", "shift": "C" },
                { "char": "d", "shift": "D" }
            ]
        ],
        [
            [
                { "char": "e", "shift": "E" },
                { "char": "f", "shift": "F" }
            ]
        ]
    ]
    ```


## Custom client assets

For some customization features of Tekst, it is necessary to provide custom assets to the client application. So if you want to e.g. use [additional fonts](#additional-custom-fonts) or the [on-screen keyboard](#on-screen-keyboard) feature with custom key maps, this is a preparation step you'll have to take.

To provide custom assets, you need administrative access to the server on which the platform application is deployed. The procedure is described step by step below.

!!! warning

    It is always recommended to create a backup of all application data before making any changes to the application deployment!


**For a Docker-based deployment...**

1. In case you haven't done so already, in the `.env` file, set the value for `TEKST_WEB_STATIC_DIR` to a path under which you want to make additional static files available for the web client (e.g., `/var/www/tekst/static/`) and create the corresponding directories.
2. For the client container to recognize the changed value in `.env`, it needs to be restarted (`docker compose restart client`).


**For a bare-metal deployment...**

1. In case you haven't done so already, create a directory where you want to make additional static files available for the web client (e.g., `/var/www/tekst/static/`).
2. Ensure that your web server makes this directory available as `/static` under the same path as the application, e.g `www.tekst-platform.org/static`. How this is done depends on the web server you are using.
