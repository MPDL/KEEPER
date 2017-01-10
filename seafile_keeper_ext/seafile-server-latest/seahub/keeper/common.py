# -*- coding: utf-8 -*-

import os

from seahub.profile.models import Profile

import mistune

def get_user_name(user):
    """Get user name"""
    # default name is user id
    name = user
    p = Profile.objects.get_profile_by_user(user)
    if p and p.nickname:
        name = p.nickname
    return name

HEADER_STEP = 2
# Headers in MD file to be processed by the parse_markdown
md_headers =  ['Title', 'Author', 'Year', 'Description', 'Institute', 'DOI', 'Comments']

class TokenTreeRenderer(mistune.Renderer):
    # options is required
    options = {}

    def placeholder(self):
        return []

    def __getattribute__(self, name):
        """Saves the arguments to each Markdown handling method."""
        found = TokenTreeRenderer.__dict__.get(name)
        if found is not None:
            return object.__getattribute__(self, name)

        def fake_method(*args, **kwargs):
            # return [(name, args, kwargs)]
            return [name, args]
        return fake_method

md_processor = mistune.Markdown(renderer=TokenTreeRenderer())

def parse_markdown (md):
    """Parse markdown file"""
    res = {}
    stack = []
    parsed = md_processor.render(md)

    for i in range(0, len(parsed)-1, 2):
        str = parsed[i]
        h = parsed[i+1]
        if str == 'header':
            if h[2] in md_headers and h[1] == HEADER_STEP:
                stack.append(h[2])
        elif str == 'paragraph':
            if len(stack) > 0:
                txt_list = []
                for i1 in range(0, len(h[0])-1, 2):
                    if h[0][i1] in ['text', 'autolink']:
                        txt_list.append(h[0][i1+1][0])
                val = ''.join(txt_list).strip()
                if val:
                    res[stack.pop()] = val
                else:
                    stack.pop()
    return res