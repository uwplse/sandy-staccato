package edu.washington.cse.instrumentation.runtime.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Retention(RetentionPolicy.RUNTIME)
@Target(value={ElementType.TYPE})
public @interface AutoPropagate {
	String pattern();
	String setterMethod();
	Class<?> setterOwner();
}
