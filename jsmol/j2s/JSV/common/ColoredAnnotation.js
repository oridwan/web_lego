Clazz.declarePackage("JSV.common");
Clazz.load(["JSV.common.Annotation"], "JSV.common.ColoredAnnotation", null, function(){
var c$ = Clazz.decorateAsClass(function(){
this.color = null;
Clazz.instantialize(this, arguments);}, JSV.common, "ColoredAnnotation", JSV.common.Annotation);
Clazz.makeConstructor(c$, 
function(){
Clazz.superConstructor (this, JSV.common.ColoredAnnotation, []);
});
Clazz.defineMethod(c$, "getColor", 
function(){
return this.color;
});
Clazz.defineMethod(c$, "setCA", 
function(x, y, spec, text, color, isPixels, is2D, offsetX, offsetY){
this.setA(x, y, spec, text, isPixels, is2D, offsetX, offsetY);
this.color = color;
return this;
}, "~N,~N,JSV.common.Spectrum,~S,javajs.api.GenericColor,~B,~B,~N,~N");
});
;//5.0.1-v7 Thu May 08 14:17:10 CDT 2025
