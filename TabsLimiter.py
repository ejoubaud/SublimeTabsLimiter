import sublime
import sublime_plugin
import os
import time


# True if view is a preview,
# i.e. it has been clicked onin sidebar or highlighted in file search results but is not a tab yet
def is_preview(view):
    return sublime.active_window().get_view_index(view)[1] == -1


def is_active(view):
    return view.id() == sublime.active_window().active_view().id()


# Identifies the Sublime Text file search view
def is_file_search_view(view):
    return view.id() == 2


def is_closable(view):
    is_not_closable = view.is_dirty() \
                    or view.is_loading() \
                    or is_preview(view) \
                    or is_active(view)
    return not(is_not_closable)


def debug_window():
    w = sublime.active_window()
    print len(w.views())
    for v in w.views():
        print str(v) + ":" + str(v.id()) + ":" + str(v.file_name())


def debug_view(view):
    print "id      : " + str(view.id())
    print "filename: " + str(view.file_name())
    print "size    : " + str(view.size())
    print "preview : " + str(is_preview(view))


# Monitors unsaved files to get their last access time
# Gets last access files from OS for saved files
class ViewAccessTime:

    last_access_by_view_id = {}

    def touch(self, view):
        if not view.file_name():
            self.last_access_by_view_id[view.id()] = time.time()

    def unregister(self, view):
        vid = view.id()
        if vid in self.last_access_by_view_id:
            del(self.last_access_by_view_id[vid])

    def last_access(self, view):
        path = view.file_name()
        vid = view.id()
        if path:
            return os.path.getatime(path)
        elif vid in self.last_access_by_view_id:
            return self.last_access_by_view_id[vid]
        else:
            return 0

    def sort_by_idle_time(self, views, asc=True):
        accesses = {}
        for view in views:
            accesses[view] = self.last_access(view)
        sorted_views = sorted(accesses, key=accesses.get, reverse=asc)
        return sorted_views


class TabsLimiter(sublime_plugin.EventListener):

    # Settings
    limit = False
    is_limit_by_group = False
    close_order = "old"

    # States
    last_loaded_view_id = -1
    is_file_search_on = False

    # Internal helpers
    views_access = ViewAccessTime()

    def on_new(self, view):
        self.views_access.touch(view)
        self.limit_tabs()

    def on_load(self, view):
        # If preview from file search, we close it only when confirmed, cf. #on_activation
        if self.is_file_search_on:
            self.last_loaded_view_id = view.id()
        # If preview from sidebar, a Sublime bug forbids changing focus on_activation,
        # so we handle tab limitation on load
        else:
            self.limit_tabs()

    def on_deactivated(self, view):
        # We need to differenciate between sidebar preview and file search preview, cf. #on_load
        if is_file_search_view(view):
            self.is_file_search_on = False

    def on_activated(self, view):
        self.views_access.touch(view)
        # We need to differenciate between sidebar preview and file search preview, cf. #on_load
        if is_file_search_view(view):
            self.is_file_search_on = True
        # If loaded from file search, we close it now that it's activated
        elif (view.id() == self.last_loaded_view_id
              and not is_preview(view)):
            self.last_loaded_view_id = -1
            self.limit_tabs()

    def on_post_save(self, view):
        # Only unsaved files need to be handeld by views_accessg169

        self.views_access.unregister(view)

    # Fetches settings and launches appropriate closing method (group or window)
    def limit_tabs(self):
        self.parse_settings()
        # If no setting for limit (or limit 0), we stop everything
        if not(self.limit):
            return False
        window = sublime.active_window()
        closed = self.limit_current_group_tabs(window)
        if not(self.is_limit_by_group) and not(closed):
            closed = self.limit_window_tabs(window)

    def parse_settings(self):
        settings = sublime.load_settings('TabsLimiter.sublime-settings')
        self.limit = settings.get("tab_number_limit", self.limit)
        self.is_limit_by_group = settings.get("limit_tabs_by_group", self.is_limit_by_group)
        self.close_order = settings.get("close_order", self.close_order)

    # Limits the number of tabs inside currently active group
    # Returns closed view's id if any closed, False if none
    def limit_current_group_tabs(self, window):
        group = window.active_group()
        views = window.views_in_group(group)
        if len(views) >= self.limit:
            return self.close_in_order(views)
        return False

    # Limits the number of tabs all over the current window
    def limit_window_tabs(self, window):
        views = window.views()
        if len(views) >= self.limit:
            self.close_in_order(views)

    # Closes the first closable view in the right order according to settings
    def close_in_order(self, views):
        ordered = self.order_for_closing(views)
        closable = self.find_first_closable(ordered)
        closed = False
        if closable is not None:
            self.close_view(closable)
            closed = closable.id()
        return closed

    # Sorts the views according to the close_order settings
    def order_for_closing(self, views):
        ordered = []
        if self.close_order == "left":
            ordered = views
        elif self.close_order == "right":
            ordered = list(views)
            ordered.reverse()
        elif self.close_order == "active":
            ordered = self.views_access.sort_by_idle_time(views, True)
        # Default: "inactive"
        else:
            ordered = self.views_access.sort_by_idle_time(views, False)
        return ordered

    # Iterates on views and returns the first view that is closable
    def find_first_closable(self, views):
        to_close = None
        for view in views:
            if is_closable(view):
                to_close = view
                break
        return to_close

    # Closes given view
    def close_view(self, view):
        print "TabsLimiter: auto-closing tab " + str(view.id()) + " with file " + str(view.file_name())
        window = sublime.active_window()
        window.focus_view(view)
        window.run_command("close_file")
