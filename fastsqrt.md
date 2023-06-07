+++
title = "fast inverse square root"
date = "1986-05-11 10:30PM"
+++

> source: [Fast inverse square root - Wikipedia](https://en.wikipedia.org/wiki/Fast_inverse_square_root)

Fast inverse square root, sometimes referred to as Fast InvSqrt() or by the hexadecimal constant 0x5F3759DF, is an algorithm that estimates 1/sqrt(x), the reciprocal (or multiplicative inverse) of the square root of a 32-bit floating-point number x floating-point

``` C
float Q_rsqrt( float number )
{
	long i;
	float x2, y;
	const float threehalfs = 1.5F;

	x2 = number * 0.5F;
	y  = number;
	i  = * ( long * ) &y;                       // evil floating point bit level hacking
	i  = 0x5f3759df - ( i >> 1 );               // what the fuck? 
	y  = * ( float * ) &i;
	y  = y * ( threehalfs - ( x2 * y * y ) );   // 1st iteration
//	y  = y * ( threehalfs - ( x2 * y * y ) );   // 2nd iteration, this can be removed

	return y;
}
```