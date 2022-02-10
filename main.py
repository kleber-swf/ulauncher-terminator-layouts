import os
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from configparser import ConfigParser
import re

def get_layouts(config_file):
    inside_layouts = False
    regex = r"\s*\[\[(\w[^\]]+)\]\]"
    layouts = []

    with open(config_file, 'r') as f:
        for line in f.readlines():
            if not inside_layouts:
                inside_layouts = '[layouts]' in line
                continue
            matches = re.match(regex, line)
            if matches == None:
                if line.startswith('['): break
                else: continue
            layouts.append(matches.group(1))

    return layouts


class DemoExtension(Extension):
    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        config_file = os.path.expanduser(extension.preferences['terminator_config'])
        layouts = get_layouts(config_file)

        query = event.get_argument()
        if query:
            query = query.strip().lower()
            layouts = [a for a in layouts if query in a]

        entries = []
        for layout in layouts:
            entries.append(ExtensionResultItem(
                name=layout,
                icon='images/icon.png',
                description=layout + ' layoutt',
                on_enter=ExtensionCustomAction({ 'layout': layout })
            ))

        return RenderResultListAction(entries)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        l = event.get_data()['layout']
        cmd = extension.preferences['terminator_cmd'].split(' ') + ['--layout={0}'.format(l)]
        print(cmd)
        subprocess.Popen(cmd)


if __name__ == '__main__':
    DemoExtension().run()
