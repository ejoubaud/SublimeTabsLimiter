import sublime
import sublime_plugin


class TabsLimiter(sublime_plugin.EventListener):

    last_loaded_view_id = -1
    is_file_search_on = False
    limit = False
    is_limit_by_group = False
    close_last_tab_first = True

    def on_new(self, view):
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
        if self.is_file_search_view(view):
            self.is_file_search_on = False

    def on_activated(self, view):
        # We need to differenciate between sidebar preview and file search preview, cf. #on_load
        if self.is_file_search_view(view):
            self.is_file_search_on = True
        # If loaded from file search, we close it now that it's activated
        elif (view.id() == self.last_loaded_view_id
              and not self.is_preview(view)):
            self.last_loaded_view_id = -1
            self.limit_tabs()

    # True if view is a preview,
    # i.e. it has been clicked onin sidebar or highlighted in file search results but is not a tab yet
    def is_preview(self, view):
        return sublime.active_window().get_view_index(view)[1] == -1

    def is_active(self, view):
        return view.id() == sublime.active_window().active_view().id()

    # Identifies the Sublime Text file search view
    def is_file_search_view(self, view):
        return view.id() == 2

    def is_closable(self, view):
        is_not_closable = view.is_dirty() \
                        or view.is_loading() \
                        or self.is_preview(view) \
                        or self.is_active(view)
        return not(is_not_closable)

    # Fetches settings and launches appropriate closing method (group or window)
    def limit_tabs(self):
        self.parse_settings()
        # If no setting for limit (or limit 0), we stop everything
        if not(self.limit):
            return False
        window = sublime.active_window()
        closed = self.limit_current_group_tabs(window)
        if not(self.is_limit_by_group) and not(closed):
            self.limit_window_tabs(window)

    def parse_settings(self):
        settings = sublime.load_settings('TabsLimiter.sublime-settings')
        self.limit = settings.get("tab_number_limit")
        self.is_limit_by_group = settings.get("limit_tabs_by_group")
        self.close_last_tab_first = settings.get("close_last_tab_first")

    # Limits the number of tabs inside currently active group
    # Returns closed view's id if any closed, False if none
    def limit_current_group_tabs(self, window):
        group = window.active_group()
        views = window.views_in_group(group)
        if len(views) >= self.limit:
            return self.close_first_clean_tab(window, views)
        return False

    # Limits the number of tabs all over the current window
    def limit_window_tabs(self, window):
        views = window.views()
        if len(views) >= self.limit:
            self.close_first_clean_tab(window, views)

    # Closes the first view that is not dirty
    # Returns closed view's id if any closed, False if none
    def close_first_clean_tab(self, window, views):
        rviews = list(views)
        if self.close_last_tab_first:
            rviews.reverse()
        closed = False
        for view in rviews:
            if self.is_closable(view):
                closed = view.id()
                self.close_view(view, window)
                break
        return closed

    # Closes given view
    def close_view(self, view, window):
        print "TabsLimiter: auto-closing tab " + str(view.id()) + " with file " + str(view.file_name())
        window.focus_view(view)
        window.run_command("close_file")

    def debug_window(self):
        w = sublime.active_window()
        print len(w.views())
        for v in w.views():
            print str(v) + ":" + str(v.id()) + ":" + str(v.file_name())

    def debug_view(self, view):
        print "id      : " + str(view.id())
        print "filename: " + str(view.file_name())
        print "size    : " + str(view.size())
        print "preview : " + str(self.is_preview(view))
        print "last_act: " + str(self.last_loaded_view_id)
