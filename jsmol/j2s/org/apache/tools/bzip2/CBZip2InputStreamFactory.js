Clazz.declarePackage("org.apache.tools.bzip2");
Clazz.load(null, "org.apache.tools.bzip2.CBZip2InputStreamFactory", ["org.apache.tools.bzip2.CBZip2InputStream"], function(){
var c$ = Clazz.declareType(org.apache.tools.bzip2, "CBZip2InputStreamFactory", null);
Clazz.defineMethod(c$, "getStream", 
function(is){
is.read( Clazz.newByteArray (2, 0), 0, 2);
return  new org.apache.tools.bzip2.CBZip2InputStream(is);
}, "java.io.InputStream");
});
;//5.0.1-v7 Thu May 08 14:17:10 CDT 2025
