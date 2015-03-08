# Copyright 2014-2015, Tresys Technology, LLC
#
# This file is part of SETools.
#
# SETools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 2.1 of
# the License, or (at your option) any later version.
#
# SETools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with SETools.  If not, see
# <http://www.gnu.org/licenses/>.
#
import re

from . import compquery


class TypeQuery(compquery.ComponentQuery):

    """Query SELinux policy types."""

    def __init__(self, policy,
                 name="", name_regex=False,
                 alias="", alias_regex=False,
                 attrs=set(), attrs_equal=False, attrs_regex=False,
                 permissive=False, match_permissive=False):
        """
        Parameter:
        policy	            The policy to query.
        name                The type name to match.
        name_regex          If true, regular expression matching
                            will be used on the type names.
        alias               The alias name to match.
        alias_regex         If true, regular expression matching
                            will be used on the alias names.
        attrs               The attribute to match.
        attrs_equal         If true, only types with attribute sets
                            that are equal to the criteria will
                            match.  Otherwise, any intersection
                            will match.
        attrs_regex         If true, regular expression matching
                            will be used on the attribute names instead
                            of set logic.
        match_permissive    If true, the permissive state will be matched.
        permissive          The permissive state to match.
        """

        self.policy = policy
        self.set_name(name, regex=name_regex)
        self.set_alias(alias, regex=alias_regex)
        self.set_attrs(attrs, regex=attrs_regex, equal=attrs_equal)
        self.set_permissive(match_permissive, permissive=permissive)

    def results(self):
        """Generator which yields all matching types."""

        for t in self.policy.types():
            if self.name and not self._match_name(t):
                continue

            if self.alias and not self._match_in_set(
                    t.aliases(),
                    self.alias_cmp,
                    self.alias_regex):
                continue

            if self.attrs and not self._match_regex_or_set(
                    set(t.attributes()),
                    self.attrs_cmp,
                    self.attrs_equal,
                    self.attrs_regex):
                continue

            if self.match_permissive and t.ispermissive != self.permissive:
                continue

            yield t

    def set_alias(self, alias, **opts):
        """
        Set the criteria for the type's aliases.

        Parameter:
        alias       Name to match the component's aliases.

        Keyword Options:
        regex       If true, regular expression matching will be used.

        Exceptions:
        NameError   Invalid keyword option.
        """

        self.alias = alias

        for k in list(opts.keys()):
            if k == "regex":
                self.alias_regex = opts[k]
            else:
                raise NameError("Invalid alias option: {0}".format(k))

        if not self.alias:
            self.alias_cmp = None
        elif self.alias_regex:
            self.alias_cmp = re.compile(self.alias)
        else:
            self.alias_cmp = self.alias

    def set_attrs(self, attrs, **opts):
        """
        Set the criteria for the type's attributes.

        Parameter:
        alias 		Name to match the component's attributes.

        Keyword Options:
        regex       If true, regular expression matching will be used
                    instead of set logic.
        equal		If true, the attribute set of the type
                    must equal the attributes criteria to
                    match. If false, any intersection in the
                    critera will cause a rule match.

        Exceptions:
        NameError   Invalid keyword option.
        """

        self.attrs = attrs

        for k in list(opts.keys()):
            if k == "regex":
                self.attrs_regex = opts[k]
            elif k == "equal":
                self.attrs_equal = opts[k]
            else:
                raise NameError("Invalid alias option: {0}".format(k))

        if not self.attrs:
            self.attrs_cmp = None
        elif self.attrs_regex:
            self.attrs_cmp = re.compile(self.attrs)
        else:
            self.attrs_cmp = set(self.policy.lookup_attribute(a) for a in self.attrs)

    def set_permissive(self, match, **opts):
        """
        Set if the permissive state should be matched.

        Parameter:
        match       If true, the permissive state will be matched.
        permissive  If true, permissive types will match, otherwise
                    enforcing types will match.

        Exceptions:
        NameError   Invalid keyword option.
        """

        self.match_permissive = bool(match)

        for k in list(opts.keys()):
            if k == "permissive":
                self.permissive = bool(opts[k])
            else:
                raise NameError("Invalid permissive option: {0}".format(k))
