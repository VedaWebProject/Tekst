# Customization

## Additional Fonts for Resources

You can provide yourself and other users with the option to use alternative fonts for specific resources. This can be useful when the content of a resource uses a specific character set or diacritics that cannot be displayed by the default font for content.

To add additional fonts for resources, you need administrative access to the server on which the platform application is deployed. The setup of additional fonts is precisely described below. It is always recommended to create a backup of all application data before performing these steps.


**For Docker-based deployment...**

1. In case you haven't done so already, in the `.env` file, set the value for `TEKST_WEB_STATIC_FILES` to a path under which you want to make additional static files available for the web client (e.g., `/var/www/tekst/static/`) and create the corresponding directories.
2. Create a file `fonts.css` under this path.
3. Also, create a folder `fonts` under this path, where you can store the additional fonts (possibly sorted into further subfolders). It is recommended to prepare each font in different formats optimized for web use (see also [here](https://developer.mozilla.org/en-US/docs/Learn/CSS/Styling_text/Web_fonts)!). Also, pay attention to the licensing of the fonts used and, if necessary, include the corresponding license file with the files.
4. In the previously created `fonts.css`, create a complete `@font-face` definition for each of your fonts. See [here](https://developer.mozilla.org/en-US/docs/Learn/CSS/Styling_text/Web_fonts) again for details. As the public path to the files, specify `/static/fonts/<...>`, replacing `<...>` with the path within your previously created `fonts` folder.
5. For the application to recognize the changed value in `.env`, it needs to be restarted (`docker-compose restart client`).
6. The value used for `font-family` in the `@font-face` definition can now be entered as an additional font in the platform's system settings. Pay attention to identical spelling! This font can now be selected as a different font in the settings for each text-based resource.


**For bare-metal deployment...**

1. In case you haven't done so already, create a directory where you want to make additional static files available for the web client (e.g., `/var/www/tekst/static/`) and ensure that your web server makes this directory available as `/static` at the same address as the application, for example, `www.tekst-platform.org/static`.
2. Follow steps **2.** to **4.**, and **6.** from the _Deployment with Docker_ instructions (see above).
