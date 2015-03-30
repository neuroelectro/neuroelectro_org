#!/usr/bin/env python
"""
    ---------------------------------------------------
    Extract Abbrevations from English Sentenece.
    Develpoed and maintained by Narayana Perumal.G
    under GPL Licenec. v0.99
    mail : gnperumal@gmail.com
    Sr.Programmer in Serene Informatics, Chennai, India.
    ----------------------------------------------------
"""
import re
class ExtractAbbrev:
    def __init__(self):
        self.abbrevdict={}    
    
    def __isThere(self, sKey):
        if sKey=="":
            return 0
        if sKey in self.abbrevdict:
            return 1
        else:
            return 0
        
    def __isValidShortForm(self, str):
        """
            It's check weather is valid shortform of abbrevation
            @param : string
            @return : if valid true other than false
        """
        if(self.__hasLetter(str) and (str[0].isalpha() or (str[0] == '('))):
            return 1
        return 0
    def __hasLetter(self, str):
        """
            Checking the following string contains a alpha character.
            @param : string
            @return : if valid true other than false
        """
        for ch in str:
            if(ch.isalpha()):
                return 1
        return 0
    def __hasCapital(self, str):
        """
            Checking the following string contains a upper case letter.
            @param : string
            @return : if valid true other than false
        """
        for ch in str:
            if(ch.isupper()):
                return 1
        return 0
    def __findbestlongform(self, shortForm, longForm):
        """
            To find the best long form from the raw long form string
            @param : (string) shortForm, longForm
            @return : (string) bestLongForm 
        """
        sIndex=len(shortForm)-1
        lIndex=len(longForm)-1
        for i in range(sIndex,-1,-1):
            currChar=shortForm[i].lower()
            if not currChar.isalnum():
                continue
            while ((lIndex>=0) and 
                   (not longForm[lIndex].lower()==currChar) or 
                   (sIndex==0) and (lIndex>0) and
                   (longForm[lIndex-1].isalnum())):
                   lIndex-=1
            if lIndex<0:
                return
            lIndex-=1
        lIndex=longForm[:lIndex].rindex(" ")+1;
        return longForm[lIndex:]
    
    def __extractabbrpair(self,shortForm,longForm):
        """
        """
        if len(shortForm)==1:
            return
        bestLongForm=self.__findbestlongform(shortForm, longForm)
        if(bestLongForm==""):
            return
        shortFormSize=len(shortForm)        
        longFormSize=len(re.split(r'\r|\n|\r|\f|-', bestLongForm))
        for i in (shortFormSize-1,-1-1):
            if not shortForm[i].isalnum():
                shortFormSize=shortFormSize-1
        if (len(bestLongForm)<len(shortForm) or 
            bestLongForm.find(shortForm+" ")>-1 or
            bestLongForm.endswith(shortForm) or
            longFormSize > shortFormSize * 2 or
            longFormSize > shortFormSize + 5 or
            shortFormSize > 10):
            return
        else:
            if not self.__isThere(shortForm):
                self.abbrevdict[shortForm]=bestLongForm
                        
    def extractabbrpairs(self, sent):
#        abbrevdict={}        
        (closeParenIndex, tmpIndex)=-1,-1
        currSentence=sent   
        try:
            while True:
                openParenIndex=currSentence.find(' (')
                if not (openParenIndex>-1): break
                if openParenIndex >- 1: 
                    openParenIndex += 1            
                sentenceEnd=max(currSentence.rfind(". "), currSentence.rfind(", "))
                if((openParenIndex==-1) and (sentenceEnd==-1)):pass
                elif(openParenIndex==-1):
                    currSentence=currSentence[sentenceEnd+2:]                
                closeParenIndex=currSentence.index(")", openParenIndex)            
                if closeParenIndex>-1:
                    sentenceEnd=max(currSentence[:openParenIndex].rfind(". "), currSentence[:openParenIndex].rfind(", "))
                    if(sentenceEnd==-1):
                        sentenceEnd=-2
                    longForm=currSentence[sentenceEnd+2:openParenIndex]
                    shortForm=currSentence[openParenIndex+1:closeParenIndex]
                if(len(shortForm)>0 or len(longForm)>0):
                    if(len(shortForm)>1 and len(longForm)>1):
                        if(shortForm.find("(")>-1 and currSentence[:closeParenIndex + 1].find(')')>-1):
                            newcloseParenIndex=currSentence[:closeParenIndex + 1].find(')')
                            shortForm = currSentence[openParenIndex + 1:newcloseParenIndex]
                            closeParenIndex=newcloseParenIndex
                        if(shortForm.find(", ") > -1):
                            shortForm = shortForm[0: shortForm.find(", ")];
                        if(shortForm.find("; ") > -1):
                            shortForm = shortForm[0, shortForm.find(", ")];
                        if(len(shortForm.split())>2 or len(shortForm)>len(longForm)):
                            tmpIndex=currSentence[: openParenIndex - 2].rfind(" ")
                            tmpStr = currSentence[tmpIndex + 1:openParenIndex - 1];
                            longForm = shortForm;
                            shortForm = tmpStr;
                            if not self.__hasCapital(shortForm):
                                shortForm=""
                        if(self.__isValidShortForm(shortForm)):
                            self.__extractabbrpair(shortForm.strip(), longForm.strip())
                    currSentence = currSentence[closeParenIndex + 1:]
                elif(openParenIndex>-1):
                    if(len(currSentence)-openParenIndex>200):
                        currSentence = currSentence[openParenIndex + 1:]
                shortForm=""
                longForm=""
            return self.abbrevdict
        except Exception:
            return self.abbrevdict
#obj=ExtractAbbrev()
#sent="Activation of Creb results in phosphorylation of Creb binding protein (CBP). CBP in turn activates p53 through methylation."
#abr=obj.extractabbrpairs(sent)
#for k,v in abr.iteritems():
#    print "Key=>%s\tvalue=>%s"%(k,v)
    