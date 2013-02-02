<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:exsl="http://exslt.org/common"
  extension-element-prefixes="exsl"
  version="1.0">

<xsl:param name="print" select="'no'"/>
<xsl:param name="printWidth" select="0"/>

<!-- tests for aircrew dm, we dont use scroll bars on aircrew dm's-->
<xsl:variable name="acrw" select="boolean(/dmodule/content/acrw)"/>

<xsl:variable name="colspecs-firstPass-rtf">
  <xsl:for-each select="//table">
    <table id="{generate-id()}">
      <xsl:for-each select="tgroup">
        <tgroup id="{generate-id()}">
          <xsl:for-each select=".//colspec">
            <col id="{generate-id()}" colname="{@colname}"
number="{count(preceding-sibling::colspec|.)}"
width="{translate(@colwidth,'inm*','')}" align="{@align}">
              <xsl:attribute name="inHead">
                <xsl:choose>
                  <xsl:when test="parent::thead">yes</xsl:when>
                  <xsl:otherwise>no</xsl:otherwise>
                </xsl:choose>
              </xsl:attribute>
            </col>
          </xsl:for-each>
          <xsl:for-each select="spanspec">
            <spanspec id="{generate-id()}" spanname="{@spanname}"
namest="{@namest}" nameend="{@nameend}" align="{@align}"/>
          </xsl:for-each>
        </tgroup>
      </xsl:for-each>
    </table>
  </xsl:for-each>
</xsl:variable>

<xsl:variable name="colspecs-firstPass"
select="exsl:node-set($colspecs-firstPass-rtf)"/>

<xsl:variable name="colspecs-rtf">
  <xsl:for-each select="$colspecs-firstPass">
    <xsl:for-each select="table">
      <table id="{@id}">
        <xsl:for-each select="tgroup">
          <tgroup id="{@id}">
            <xsl:variable name="totalGroupWidth" select="sum(col[@inHead =
'no']/@width)"/>
            <xsl:variable name="totalHeadWidth" select="sum(col[@inHead =
'yes']/@width)"/>
            <xsl:for-each select="col">
              <col id="{@id}" colname="{@colname}" number="{@number}"
align="{@align}" inHead="{@inHead}">
                <xsl:attribute name="width">
                  <xsl:choose>
                    <xsl:when test="@inHead = 'no'">
                      <xsl:value-of select="@width div $totalGroupWidth *
100"/>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:value-of select="@width div $totalHeadWidth *
100"/>
                    </xsl:otherwise>
                  </xsl:choose>
                </xsl:attribute>
              </col>
            </xsl:for-each>
            <xsl:for-each select="spanspec">
              <xsl:copy-of select="."/>
            </xsl:for-each>
          </tgroup>
        </xsl:for-each>
      </table>
    </xsl:for-each>
  </xsl:for-each>
</xsl:variable>

<xsl:variable name="colspecs" select="exsl:node-set($colspecs-rtf)"/>

<xsl:variable name="spanspecs-rtf">
  <xsl:for-each select="$colspecs">
    <xsl:for-each select="table/tgroup">
      <xsl:variable name="tgroupId" select="@id"/>
      <xsl:for-each select="spanspec">
        <col id="{@id}" spanname="{@spanname}">
          <xsl:attribute name="colspan">
            <xsl:value-of select="1 + preceding-sibling::col[@colname =
current()/@nameend]/@number - preceding-sibling::col[@colname =
current()/@namest]/@number"/>
          </xsl:attribute>
          <xsl:attribute name="width">
            <xsl:call-template name="calculateWidth">
              <xsl:with-param name="tgroupId" select="$tgroupId"/>
              <xsl:with-param name="startCol"
select="preceding-sibling::col[@colname = current()/@namest]/@number"/>
              <xsl:with-param name="endCol"
select="preceding-sibling::col[@colname = current()/@nameend]/@number"/>
            </xsl:call-template>
          </xsl:attribute>
          <xsl:attribute name="align">
            <xsl:choose>
              <xsl:when test="string-length(@align)"><xsl:value-of
select="@align"/></xsl:when>
              <xsl:otherwise><xsl:value-of
select="preceding-sibling::col[@colname =
current()/@nameend]/@align"/></xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </col>
      </xsl:for-each>
    </xsl:for-each>
  </xsl:for-each>
</xsl:variable>

<xsl:variable name="spanspecs" select="exsl:node-set($spanspecs-rtf)"/>

<xsl:template name="calculateWidth">
  <xsl:param name="tgroupId" select="0"/>
  <xsl:param name="startCol" select="0"/>
  <xsl:param name="endCol" select="0"/>
  <xsl:param name="totalWidth" select="0"/>
  <xsl:choose>
    <xsl:when test="$startCol &lt;= $endCol">
      <xsl:call-template name="calculateWidth">
        <xsl:with-param name="tgroupId" select="$tgroupId"/>
        <xsl:with-param name="startCol" select="$startCol + 1"/>
        <xsl:with-param name="endCol" select="$endCol"/>
        <xsl:with-param name="totalWidth">
          <xsl:for-each select="$colspecs">
            <xsl:for-each select="table/tgroup[@id = $tgroupId]">
              <xsl:value-of select="col[@number = $startCol]/@width +
$totalWidth"/>
            </xsl:for-each>
          </xsl:for-each>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$totalWidth"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="getBorders">
  <xsl:param name="frame" select="''"/>
  <xsl:choose>
    <xsl:when test="$frame = 'ALL'">t b l r</xsl:when>
    <xsl:when test="$frame = 'TOP'">t</xsl:when>
    <xsl:when test="$frame = 'TOPBOT'">t b</xsl:when>
    <xsl:when test="$frame = 'BOTTOM'">b</xsl:when>
    <xsl:when test="$frame = 'SIDES'">l r</xsl:when>
    <xsl:when test="$frame = 'NONE'">t b l r</xsl:when>
    <xsl:otherwise>t b l r</xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template match="table">
  <xsl:variable name="tableFrame">
     <xsl:call-template name="getBorders">
       <xsl:with-param name="frame" select="@frame"/>
     </xsl:call-template>
  </xsl:variable>

  <div>
    <xsl:apply-templates>
      <xsl:with-param name="tableFrame" select="$tableFrame"/>
    </xsl:apply-templates>
  </div>
</xsl:template>

<xsl:template match="tgroup">
  <xsl:param name="tableFrame"/>
  <xsl:variable name="tgroupId" select="generate-id()"/>
  <!--When the table is dead on 300 high IE can get caught in a dependency
loop if we set the 'else'
      value to 'scrollHeight', so instead we use the dummy string 'nause' to
do nothing, because it
      was a right nause finding and fixing the bug... -->
  <div class="{$tableFrame}">
    <xsl:attribute name="style">
      <xsl:text>width:100%;</xsl:text>
      <xsl:if 
 test="$print = 'no'">overflow:auto;height:expression(scrollHeight >= 300 ? 300 :
'nause');</xsl:if>
    </xsl:attribute>
    <xsl:if test="$print = 'no' and .//thead">
      <xsl:attribute
name="onscroll">nextSibling.scrollLeft=scrollLeft</xsl:attribute>
    </xsl:if>
   <table cellpadding="3" cellspacing="0" style="width:100%">
     <colgroup>
       <xsl:for-each select="$colspecs">
         <xsl:for-each select="table/tgroup[@id = $tgroupId]/col[@inHead =
'no']">
           <col width="{@width}%"/>
         </xsl:for-each>
       </xsl:for-each>
     </colgroup>
     <xsl:if test="thead">
     <thead>
     <xsl:for-each select="thead/row">
       <tr>
         <xsl:apply-templates select="entry">
           <xsl:with-param name="inHead" select="'true'"/>
           <xsl:with-param name="fakey" select="'true'"/>
           <xsl:with-param name="tgroupId" select="$tgroupId"/>
         </xsl:apply-templates>
       </tr>
     </xsl:for-each>
     </thead>
     </xsl:if>

     <tbody>
     <xsl:apply-templates select="tbody">
       <xsl:with-param name="tgroupId" select="$tgroupId"/>
     </xsl:apply-templates>
     </tbody>
   </table>
  </div>
  <xsl:if test="$print = 'no' and .//thead">
  <div class="t b {$tableFrame}">
    <xsl:attribute name="style">
      <xsl:text>position:relative;
 
background-color:expression(document.body.currentStyle.backgroundColor);
                overflow:hidden;
 
top:expression(-previousSibling.clientHeight-((previousSibling.scrollWidth>p
reviousSibling.clientWidth)?18:2));</xsl:text>
      <xsl:choose>
        <!--take into account border widths-->
        <xsl:when test="contains($tableFrame,'l
r')">width:expression(previousSibling.clientWidth + 2)</xsl:when>
 
<xsl:otherwise>width:expression(previousSibling.clientWidth)</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
   <div style="width:expression(parentNode.previousSibling.scrollWidth)">
    <table cellSpacing="0" cellpadding="3" style="width:100%">
    <xsl:variable name="genIdh" select="generate-id()"/>
     <colgroup>
       <xsl:for-each select="$colspecs">
         <xsl:choose>
           <xsl:when test="table/tgroup[@id = 
          $tgroupId]/col[@inHead = 'yes']">
             <xsl:for-each 
      select="table/tgroup[@id = $tgroupId]/col[@inHead = 'yes']">
               <col width="{@width}%"/>
             </xsl:for-each>
           </xsl:when>
           <xsl:otherwise>
             <xsl:for-each 
          select="table/tgroup[@id = $tgroupId]/col[@inHead= 'no']">
               <col width="{@width}%"/>
             </xsl:for-each>
           </xsl:otherwise>
         </xsl:choose>
       </xsl:for-each>
     </colgroup>
     <thead>
    <xsl:for-each select="thead/row">
     <tr>
       <xsl:apply-templates select="entry">
         <xsl:with-param name="inHead" select="'true'"/>
         <xsl:with-param name="tgroupId" select="$tgroupId"/>
       </xsl:apply-templates>
     </tr>
    </xsl:for-each>
    </thead>
   </table>
  </div>
  </div>
  </xsl:if>
</xsl:template>

<xsl:template match="tbody">
  <xsl:param name="tgroupId" select="''"/>
  <xsl:apply-templates>
    <xsl:with-param name="tgroupId" select="$tgroupId"/>
  </xsl:apply-templates>
</xsl:template>

<xsl:template match="row|caprow">
  <xsl:param name="tgroupId" select="''"/>
  <xsl:param name="inHead" select="'false'"/>
  <xsl:if test="@id"><a><xsl:attribute name="name"><xsl:value-of
        select="@id"/></xsl:attribute></a></xsl:if>
  <tr>
    <xsl:apply-templates>
       <xsl:with-param name="tgroupId" select="$tgroupId"/>
       <xsl:with-param name="inHead" select="$inHead"/>
    </xsl:apply-templates>
  </tr>
</xsl:template>

<xsl:template match="entry|capentry">
  <xsl:param name="inHead" select="'false'"/>
  <xsl:param name="fakey" select="'false'"/>
  <xsl:param name="tgroupId" select="'no tgroup id generated'"/>
  <xsl:if test="@id"><a><xsl:attribute 
  name="name"><xsl:value-of 
    select="@id"/></xsl:attribute></a></xsl:if>
  <td>
    <xsl:if test="@morerows">
      <xsl:attribute name="rowspan">
        <xsl:value-of select="@morerows + 1"/>
      </xsl:attribute>
    </xsl:if>

    <xsl:choose>
      <xsl:when test="@spanname">
      <xsl:variable name="spanname" select="@spanname"/>
      <xsl:for-each select="$spanspecs">
        <xsl:attribute name="colspan">
          <xsl:value-of select="col[@spanname = $spanname]/@colspan"/>
        </xsl:attribute>
        <xsl:if test="$inHead = 'false'">
          <xsl:attribute name="width">
            <xsl:value-of 
              select="col[@spanname = $spanname]/@width"/>%<xsl:text/>
          </xsl:attribute>
        </xsl:if>
        <xsl:attribute name="align">
          <xsl:value-of select="col[@spanname = $spanname]/@align"/>
        </xsl:attribute>
      </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
       <xsl:if test="@namest">
        <xsl:variable name="nameStart" select="@namest"/>
        <xsl:variable name="nameEnd" select="@nameend"/>
        <xsl:variable name="nameStartId"
         select="generate-id(ancestor::tgroup/colspec[@colname = $nameStart])"/>
        <xsl:variable name="nameEndId"
         select="generate-id(ancestor::tgroup/colspec[@colname = $nameEnd])"/>
        <xsl:attribute name="colspan">
          <xsl:for-each select="$colspecs">
            <xsl:value-of select="1 + table/tgroup[@id = $tgroupId]/col
           [@id  = $nameEndId]/@number - table/tgroup
           [@id =  $tgroupId]/col[@id = $nameStartId]/@number"/>
          </xsl:for-each>
        </xsl:attribute>
        <xsl:if test="$inHead = 'false'">
        <xsl:attribute name="width">
          <xsl:call-template name="calculateWidth">
            <xsl:with-param name="tgroupId" select="$tgroupId"/>
            <xsl:with-param name="startCol">
              <xsl:for-each select="$colspecs">
                 <xsl:value-of select="table[@id = 
              $tgroupId]/col[@id = $nameStartId]/@number"/>
              </xsl:for-each>
            </xsl:with-param>
            <xsl:with-param name="endCol">
              <xsl:for-each select="$colspecs">
                 <xsl:value-of select="table[@id = 
                    $tgroupId]/col[@id = $nameEndId]/@number"/>
              </xsl:for-each>
            </xsl:with-param>
          </xsl:call-template>
          <xsl:text>%</xsl:text>
        </xsl:attribute>
        </xsl:if>
      </xsl:if>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:variable name="colname" select="@colname"/>
    <xsl:for-each select="$colspecs">
      <xsl:if test="table/tgroup[@id = $tgroupId]/col[@colname =
                 $colname]/@align">
          <xsl:attribute name="align">
            <xsl:value-of 
      select="table/tgroup[@id = $tgroupId]/col[@colname = $colname]/@align"/>
          </xsl:attribute>
      </xsl:if>
    </xsl:for-each>

    <xsl:if test="@align">
      <xsl:attribute name="align">
        <xsl:value-of select="@align"/>
      </xsl:attribute>
    </xsl:if>

    <xsl:attribute name="valign">
      <xsl:choose>
        <xsl:when test="@valign"><xsl:value-of select="@valign"/></xsl:when>
        <xsl:otherwise>top</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
    <xsl:attribute name="class">
      <xsl:if test="@rowsep='1' or (parent::*/@rowsep='1' and 
            $inHead = 'false')">b </xsl:if>
      <xsl:if test="@colsep='1' and following-sibling::entry">r </xsl:if>
      <xsl:if test="$inHead = 'true'">bold </xsl:if>
      <xsl:if test="$inHead = 'true' and $print != 'no'">b </xsl:if>
    </xsl:attribute>
    <xsl:if test="$fakey = 'true'">
      <xsl:attribute name="searchChar">`</xsl:attribute>
    </xsl:if>
    <xsl:apply-templates/>
    <span>
      <xsl:if test="$fakey = 'true'">
        <xsl:attribute name="searchChar">£</xsl:attribute>
      </xsl:if>
      <xsl:if test=". = ''"><xsl:text>##160;</xsl:text></xsl:if>
    </span>
  </td>
 </xsl:template>

<xsl:template match="capgrp">
  <xsl:variable name="widths-rtf">
    <xsl:for-each select="colspec">
      <col>
        <xsl:attribute name="width"><xsl:value-of
            select="translate(@colwidth,'inm*','')"/></xsl:attribute>
      </col>
    </xsl:for-each>
  </xsl:variable>
  <xsl:variable name="widths" select="exsl:node-set($widths-rtf)"/>
  <p>
    <xsl:attribute name="align"><xsl:value-of
             select="@align"/></xsl:attribute>
    <table style="width:100%">
    <colgroup>
     <xsl:for-each select="$widths">
       <xsl:variable name="total" select="sum(col/@width)"/>
       <xsl:for-each select="col">
         <col>
           <xsl:attribute name="width"><xsl:value-of 
          select="(@width div $total) * 100"/>%</xsl:attribute>
         </col>
       </xsl:for-each>
     </xsl:for-each>
    </colgroup>
    <xsl:apply-templates/>
   </table>
  </p>
</xsl:template>



<xsl:template name="colspanWidth">
  <xsl:param name="startCol" select="0"/>
  <xsl:param name="endCol" select="0"/>
  <xsl:param name="totalWidth" select="0"/>
  <xsl:param name="tgroupId" select="0"/>
  <xsl:choose>
    <xsl:when test="$startCol != $endCol">
      <xsl:call-template name="colspanWidth">
        <xsl:with-param name="startCol">
          <xsl:for-each select="$colspecs">
            <xsl:value-of select="table/tgroup[@id =
        $tgroupId]/col[preceding-sibling::col[1][@colname = $startCol]]/@colname"/>
          </xsl:for-each>
        </xsl:with-param>
        <xsl:with-param name="endCol" select="$endCol"/>
        <xsl:with-param name="tgroupId" select="$tgroupId"/>
        <xsl:with-param name="totalWidth">
          <xsl:for-each select="$colspecs">
            <xsl:value-of select="table/tgroup[@id = 
              $tgroupId]/col[@colname= $startCol]/@width + $totalWidth"/>
          </xsl:for-each>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$totalWidth"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet>