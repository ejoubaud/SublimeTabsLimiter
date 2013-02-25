Sublime Tabs Limiter
====================

### Description

Once you reach a certain number of tabs, they become useless. You can't even see their name properly, nor remember which one is where and contains what.

This plugin works a bit like iPad's Safari. It will automatically replace older tabs when you open a new one, so you don't overreach a configurable limit.

Its target is focus and peace of mind, so **it will never close any tab with unsaved work**, nor display any notification. If you have nothing but tabs with unsaved work, it will just ignore the limit and create a new tab anyway.

### Installation

The most straightforward installation method is via [Will Bond's](http://wbond.net/) [Package Control](http://wbond.net/sublime_packages/package_control/package_developers). If you prefer, you can also clone (or copy the contents of) this repository into your Sublime Text `./Packages` folder:

    git clone https://github.com/ejoubaud/SublimeTabsLimiter.git

### Configuration

For now, TabsLimiter's configuration file allows you to:

* set your own limit for the number of tabs
* limit the number of tabs in a display group, or for the whole window (the sum of all groups)
* specify the order of tabs removal:
** inactive tabs first (tabs that have been loaded/saved longer before go first)
** active tabs first (tabs that have been loaded/saved more recently go first)
** from the right (if you want to keep a handful of reference files at keyboard shortcut range)
** from the left (if have rather to keep more recent tabs over older ones)

### Limitations

#### Close on preview in sidebar

Due to a bug in SublimeText's API, it is not possible to close other tabs when opening a tab from the sidebar. So TabsLimiter has to close older tab when the preview of the file is loaded.

If you've already reached your tabs limit and just click on a file in the sidebar, it will instantly close the other file and you'll have to click again to display the preview. The same goes double-click, the first will close a tab, and only the second will open the new one.

Preview/loading from the Sublime's file search doesn't have this problem.

#### Limit can be violated

This is a feature, but the limit you set is not an absolute boundary.

This is a focus tool, so we want to avoid distraction and favour peace of mind. So, TabsLimiter will never close any unsaved tab, nor display any alert or notification.

The result is that when you've reached the tab limit, but no tab can be closed because they all contain unsaved work, a new tab will just be created, ignoring the limit.

