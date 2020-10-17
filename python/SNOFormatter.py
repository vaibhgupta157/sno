import lxml.etree
from xmldiff import formatting, main

import json
import re

from collections import namedtuple
from copy import deepcopy
from lxml import etree
from xmldiff.diff_match_patch import diff_match_patch
from xmldiff import utils

DIFF_NS = "http://namespaces.shoobx.com/diff"
DIFF_PREFIX = "diff"

INSERT_NAME = "{%s}insert" % DIFF_NS
DELETE_NAME = "{%s}delete" % DIFF_NS
RENAME_NAME = "{%s}rename" % DIFF_NS

# Flags for whitespace handling in the text aware formatters:
WS_BOTH = 3  # Normalize ignorable whitespace and text whitespace
WS_TEXT = 2  # Normalize whitespace only inside text tags
WS_TAGS = 1  # Delete ignorable whitespace (between tags)
WS_NONE = 0  # Preserve all whitespace

# Placeholder tag type
T_OPEN = 0
T_CLOSE = 1
T_SINGLE = 2

# This is the start of the BMP(0) private use area.
# If you end up having more than 6400 different tags inside text tags
# this will bleed over to non private use area, but that's highly
# unlikely. However, once we have dropped support for Python versions
# that have narrow builds, we can change this to 0xf00000, which is
# the start of two 64,000 private use blocks.
# PY3: Once Python 2.7 support is dropped we should change this to 0xf00000
PLACEHOLDER_START = 0xE000


# These Bases can be abstract baseclasses, but it's a pain to support
# Python 2.7 in that case, because there is no abc.ABC. Right now this
# is just a description of the API.

XSLT1 = u'''<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
    xmlns:diff="http://namespaces.shoobx.com/diff"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="@diff:insert-formatting">
        <xsl:attribute name="class">
        <xsl:value-of select="'insert-formatting'"/>
        </xsl:attribute>
    </xsl:template>

    <xsl:template match="diff:delete">
        <del><xsl:apply-templates /></del>
    </xsl:template>

    <xsl:template match="diff:insert">
        <ins><xsl:apply-templates /></ins>
    </xsl:template>

    <xsl:template match="@* | node()">
        <xsl:copy>
        <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>'''


XSLT = u'''<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
    xmlns:diff="http://namespaces.shoobx.com/diff"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">

    <xsl:template match="@diff:insert-formatting">
        <xsl:attribute name="class">
        <xsl:value-of select="'insert-formatting'"/>
        </xsl:attribute>
    </xsl:template>


    <xsl:template match="@diff:delete">
        <xsl:attribute name="nc:operation">
	    <xsl:value-of select="'delete'"/><xsl:apply-templates />
	    </xsl:attribute>
    </xsl:template>

    <xsl:template match="diff:insert">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="@* | node()">
        <xsl:copy>
        <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>'''

XSLT_TEMPLATE = lxml.etree.fromstring(XSLT1)

class SNOFormatter(formatting.XMLFormatter):
    def render(self, result):
        transform = lxml.etree.XSLT(XSLT_TEMPLATE)
        result = transform(result)
        return super(SNOFormatter, self).render(result)

'''   
    def _handle_UpdateTextIn(self, action, tree):
        node = self._xpath(tree, action.node)
        if INSERT_NAME in node.attrib:
            # The whole node is already marked as inserted,
            # we don't need to diff-wrap the text.
            node.text = action.text
            return node
        left_value = node.text
        right_value = action.text

        #print (left_value)
        #print (right_value)
        #node.text = None

        #print (dir(node))
        #print (dir(action))
        self._handle_DeleteNode(action, tree)
        self._handle_InsertNode(action, tree)

        #self._make_diff_tags(left_value, right_value, node)

        

        #return node

    def _handle_DeleteNode(self, action, tree):
        node = self._xpath(tree, action.node)
        print (node.text)
        self._delete_node(node)
'''