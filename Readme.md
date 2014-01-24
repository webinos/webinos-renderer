# webinos renderer #

This is the webinos webkit based renderer to display widgets.

## Build instructions ##

In order to build webinos widget render, please follow the [instructions in our developer portal](https://developer.webinos.org/building-webinos-widget-renderer).

Note that the current codebase is based on the [1271 branch of CEF3](http://code.google.com/p/chromiumembedded/source/browse/#svn%2Fbranches%2F1271%2Fcef3).
 
### Notes for win8 with vs 2010###

Make sure you have at least 22Gb of free hard disk.

Install the [Windows 7 SDK](http://www.microsoft.com/en-us/download/details.aspx?id=8279), [June 2010 DirectX SDK](http://www.microsoft.com/en-us/download/details.aspx?displaylang=en&id=6812) and the [Windows 8 SDK](http://msdn.microsoft.com/en-us/windows/hardware/hh852363.aspx). If you have [troubles installing DirectX](http://stackoverflow.com/questions/4102259/directx-sdk-june-2010-installation-problems-error-code-s1023), try uninstalling the "Microsoft Visual C++ 2010 x64 Redistributable".

Download [depot_tools.zip](https://src.chromium.org/svn/trunk/tools/depot_tools.zip) and decompress it in C:\dev\depot_tools. Open cmd in the depot_tools folder and run `gclient` to install the tools.

Add depot_tools to your PATH environment variable.

Download the cef automate script posting the following command:

    C:\dev>svn checkout http://chromiumembedded.googlecode.com/svn/branches/trunk/cef3/tools/automate automate

Download CEF using the automate script you just downloaded:

    C:\dev>python automate/automate.py --download-dir=webinosBrowser --revision=1271 --depot-tools=depot_tools --url=http://chromiumembedded.googlecode.com/svn/branches/1271/cef3

Get some coffee and read a couple of books. This will take a long time.

If this [fails](http://www.magpcss.org/ceforum/viewtopic.php?f=6&t=11097) in a sourceforge svn url, edit chromium\<Release>\DEPS file, change the sourceforge url to `http://svn.code.sf.net/p/<repo name>/code` and the [gsutil](https://code.google.com/p/chromium/issues/detail?id=334327) url to `svn://svn.chromium.org/gsutil/`.

Then post a `gclient sync --jobs 8 --force` command in the chromium folder to continue, and then run the automate.py command again to add the cef lib (change the 8 jobs number with the number of virtual cpus in your system).

If it still fails while gyp tries to generate your project, you will have to set the environment variable `GYP_MSVS_VERSION` to your vs version (vs 2013 won't work as the bundled gyp doesn't know where to locate the folder and you will get an error about the `2013` key), e.g:

    Set GYP_MSVS_VERSION=2010

If during the execution of `cef_create_projects`, you get an 

> Exception: Environment variable "SYSTEMROOT" required to be set to valid path

This means you are either not running in a visual studio command prompt or that you haven't set the GYP_MSVS_VERSION.

In order to compile CEF you can open the generated sln file or from command prompt, you will have to run:

    C:\dev\webinosBrowser\chromium\src\cef\tools>build_projects.bat Debug

If you want to rebuild, remove the Debug or Release folder from chromium\src\build and run the `build_projects.bat` again (you might find helpful [this tip on deleting files](http://botsikas.blogspot.gr/2014/01/deleting-multiple-small-files-fast-on.html)). 
    
If everything is fine, you should have the minimal cef browser in webinosBrowser\chromium\src\out\Debug\cefclient.exe.

Now it's time to patch cef toolchain in order to produce the webinos browser.

Copy the files from this repository inside the chromium\src\cef\ folder, replacing the gclient's hook.

In order to generate the new webinosBrowser project, go to chromium\src\cef\ and type:

    cef_create_projects.bat

Build with either visual studio, or using the command prompt as described above. The final webinosBrowser.exe will be located next to the cefclient.exe.

#### Notes for vs 2012 ####

Visual studio 2012 is not supported as there are a lot of breaking changes in the C++ compiler. If you are determined to use vs2012, you can try solving the issues using various patches and updates from the latest [chromium trunk](https://src.chromium.org/viewvc/chrome/trunk/).

The most important problem you will face is the uninitialized warnings that are treated as errors. Although you could fix all warnings, most of them are about uninitialized pointers, so you can disable the warn as error option (/WX flag) as a shortcut:

- Replace the wtl's atlapp.h file with the one in the [corresponding fix](https://src.chromium.org/viewvc/chrome?view=revision&revision=161168). 
- Apply the [VC11 patch described in this post](https://code.google.com/p/protobuf/issues/detail?id=388). 
- Replace `'WarnAsError': 'true'` with `'WarnAsError': 'false'` in all `*.gyp*` files
- Edit chromium\src\build\common.gypi and set `'win_third_party_warn_as_error%': 'false'`
- Add a `#include <functional>` on top of `\chromium\src\webkit\quota\quota_manager.cc` and `chromium\src\webkit\appcache\appcache_service.cc`
- Regenerate all projects using `gclient runhooks` inside the chromium folder.

If you want to fix the uninitialized warning instead of disabling the /WX flag, here is a list to start with (there are a lot more): 

- Patch the method Buffer CommandBufferProxyImpl::GetTransferBuffer(int32 id) in src/content/common/gpu/client/command_buffer_proxy_impl.cc with the [one in the trunk](https://src.chromium.org/viewvc/chrome/trunk/src/content/common/gpu/client/command_buffer_proxy_impl.cc).
- Modify chromium\src\content\renderer\render_thread_impl.cc lin 737 and set it to `base::SharedMemoryHandle mem_handle = NULL;`
- Modify chromium\src\base\third_party\dmg_fp\dtoa.cc line 3572 and set it to `Bigint *b, *b1, *delta, *mlo= NULL, *mhi, *S ;`

## FAQ ##

*No mp3 support*: CEF only supports open formats for codecs. See discussion in the [corresponding bug report](http://code.google.com/p/chromiumembedded/issues/detail?id=371).

