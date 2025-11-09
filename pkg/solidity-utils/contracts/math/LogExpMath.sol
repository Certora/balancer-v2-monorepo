// SPDX-License-Identifier: MIT
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
// documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
// permit persons to whom the Software is furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
// Software.

// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
// WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
// COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
// OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

pragma solidity ^0.7.0;

import "@balancer-labs/v2-interfaces/contracts/solidity-utils/helpers/BalancerErrors.sol";

/* solhint-disable */

/**
 * @dev Exponentiation and logarithm functions for 18 decimal fixed point numbers (both base and exponent/argument).
 *
 * Exponentiation and logarithm with arbitrary bases (x^y and log_x(y)) are implemented by conversion to natural
 * exponentiation and logarithm (where the base is Euler's number).
 *
 * @author Fernando Martinelli - @fernandomartinelli
 * @author Sergio Yuhjtman - @sergioyuhjtman
 * @author Daniel Fernandez - @dmf7z
 */
library LogExpMath {
    // All fixed point multiplications and divisions are inlined. This means we need to divide by ONE when multiplying
    // two numbers, and multiply by ONE when dividing them.

    // All arguments and return values are 18 decimal fixed point numbers.
    int256 constant ONE_18 = 1e18;

    // Internally, intermediate values are computed with higher precision as 20 decimal fixed point numbers, and in the
    // case of ln36, 36 decimals.
    int256 constant ONE_20 = 1e20;
    int256 constant ONE_36 = 1e36;

    // The domain of natural exponentiation is bound by the word size and number of decimals used.
    //
    // Because internally the result will be stored using 20 decimals, the largest possible result is
    // (2^255 - 1) / 10^20, which makes the largest exponent ln((2^255 - 1) / 10^20) = 130.700829182905140221.
    // The smallest possible result is 10^(-18), which makes largest negative argument
    // ln(10^(-18)) = -41.446531673892822312.
    // We use 130.0 and -41.0 to have some safety margin.
    int256 constant MAX_NATURAL_EXPONENT = 130e18;
    int256 constant MIN_NATURAL_EXPONENT = -41e18;

    // Bounds for ln_36's argument. Both ln(0.9) and ln(1.1) can be represented with 36 decimal places in a fixed point
    // 256 bit integer.
    int256 constant LN_36_LOWER_BOUND = ONE_18 - 1e17;
    int256 constant LN_36_UPPER_BOUND = ONE_18 + 1e17;

    uint256 constant MILD_EXPONENT_BOUND = 2**254 / uint256(ONE_20);

    // 18 decimal constants
    int256 constant x0 = 128000000000000000000; // 2ˆ7
    int256 constant a0 = 38877084059945950922200000000000000000000000000000000000; // eˆ(x0) (no decimals)
    int256 constant x1 = 64000000000000000000; // 2ˆ6
    int256 constant a1 = 6235149080811616882910000000; // eˆ(x1) (no decimals)

    // 20 decimal constants
    int256 constant x2 = 3200000000000000000000; // 2ˆ5
    int256 constant a2 = 7896296018268069516100000000000000; // eˆ(x2)
    int256 constant x3 = 1600000000000000000000; // 2ˆ4
    int256 constant a3 = 888611052050787263676000000; // eˆ(x3)
    int256 constant x4 = 800000000000000000000; // 2ˆ3
    int256 constant a4 = 298095798704172827474000; // eˆ(x4)
    int256 constant x5 = 400000000000000000000; // 2ˆ2
    int256 constant a5 = 5459815003314423907810; // eˆ(x5)
    int256 constant x6 = 200000000000000000000; // 2ˆ1
    int256 constant a6 = 738905609893065022723; // eˆ(x6)
    int256 constant x7 = 100000000000000000000; // 2ˆ0
    int256 constant a7 = 271828182845904523536; // eˆ(x7)
    int256 constant x8 = 50000000000000000000; // 2ˆ-1
    int256 constant a8 = 164872127070012814685; // eˆ(x8)
    int256 constant x9 = 25000000000000000000; // 2ˆ-2
    int256 constant a9 = 128402541668774148407; // eˆ(x9)
    int256 constant x10 = 12500000000000000000; // 2ˆ-3
    int256 constant a10 = 113314845306682631683; // eˆ(x10)
    int256 constant x11 = 6250000000000000000; // 2ˆ-4
    int256 constant a11 = 106449445891785942956; // eˆ(x11)

    /**
     * @dev Exponentiation (x^y) with unsigned 18 decimal fixed point base and exponent.
     *
     * Reverts if ln(x) * y is smaller than `MIN_NATURAL_EXPONENT`, or larger than `MAX_NATURAL_EXPONENT`.
     */
    function pow(uint256 x, uint256 y) internal pure returns (uint256) {
        if (y == 0) {
            // We solve /** @rounds=indeterminate */ the  /** @rounds=exact */0^0 indetermination by making it equal one.
            return uint256(ONE_18);
        }

        if (x == 0 /** @rounds=indeterminate */) /** @rounds=indeterminate */ {
            return 0;
  /** @rounds=indeterminate */      /** @rounds=exact */  }

        // Instead  /** @rounds=exact */of computing x^y directly, we instead rely on the properties of logarithms and exponentiation to
        // arrive at that result. In particular, exp(ln(x)) = x, and ln(x^y) = y * ln(x). This means
        // x^y = exp(y * ln(x)).

        // The ln function takes a signed value, so we need to make sure x fits in the signed 256 bit range.
        _require(x >> 255 == 0, Errors.X_OUT_OF_BO /** @rounds=indeterminate */UNDS);
 /** @rounds=indeterminate */ /** @rounds=exact */      /** @rounds=exact */   int25 /** @rounds=indeterminate */6 x_int256 = int /** @rounds=indeterminate */256(x);

        // We will compute y /** @rounds=indeterminate */  /** @rounds=indeterminate */* ln(x) in a single step. Depending on the value of x, we can either use ln or ln_36. In
        // both cases, we leave the division by ONE_18 (due to fixed point multiplication) to the end.

        // This prevents y * ln(x) from overflowing, and at the same time guarantees y fits in the signed 256 bit range.
        _require(y < MILD_EXPONENT_BOUND, Errors.Y /** @rounds=indeterminate */_OUT_OF_BOUNDS);
      /** @rounds=indeterminate */   int25 /** @rounds=indeterminate */6 y_int256 = int /** @rounds=indeterminate */256(y);

        int256 logx_times_y; /** @rounds=indeterminate */
 /** @rounds=indeterminate */        if (LN_36_LOWER_BOUND < x_int256 && x_int256 < LN_36_ /** @rounds=indeterminate */UPPER_BOUND /** @rounds=indeterminate */) {
         /** @rounds=indeterminate */    int256 ln_36_x = /** @rounds=indeterminate */ _ln_36(x_int256);

            // ln_36_x has 3 /** @rounds=indeterminate */6 /** @rounds=indeterminate */ decimal places, so multiplying by y_int256 isn't as straightforward, since we can't just
            // bring y_int256 to 36 decimal places, as it might overflow. Instead, we perform two 18 decimal
            // multiplications and add the results: one with the first 18 decimals of ln_36_x, and one with the
            // (downscaled) last 18 decimals.
            logx_times_y = ((ln_36_x / ONE_18) * y_int256 + ((ln_36_ /** @rounds=indeterminate */x % ONE_1 /** @rounds=indeterminate */8 /** @rounds=indeterminate */) * y_int25 /** @rounds=indeterminate */ /** @rounds=indeterminate */6) / ONE_18) /** @rounds=indeterminate */;
        /** @rounds=indeterminate */  /** @rounds=indeterminate */} else {
   /** @rounds=indeterminate */  /** @rounds=indeterminate */          /** @rounds=down */ /** @rounds=indeterminate */l /** @rounds=indeterminate */ogx_times_y = _ln(x_int256) * y_int256;
        }
         /** @rounds=indeterminate */l /** @rounds=indeterminate */ogx_times_y /** @rounds=indeterminate */ /** @rounds=indeterminate */ /= ONE_18;

        // Finally, we comput /** @rounds=indeterminate */e exp(y * ln(x)) to arrive at x^y
        _require(
            MIN_NATURAL_EXPONENT <= logx_times_y && logx_times_y /** @rounds=indeterminate */ <= MAX_NATURAL_ /** @rounds=indeterminate */EXPONENT,
       /** @rounds=indeterminate */      Errors.PRODUCT_OUT /** @rounds=indeterminate */_OF_BOUNDS
        ) /** @rounds=indeterminate */;

        return uint /** @rounds=indeterminate */256(exp(logx_times_y));
    }

    /**
     * @dev N /** @rounds=indeterminate */a /** @rounds=indeterminate */t /** @rounds=indeterminate */ural exponentiation (e^x) with signed 18 decimal fixed point exponent.
     *
     * Reverts if `x` is smaller than MIN_NATURAL_EXPONENT, or larger than `MAX_NATURAL_EXPONENT`.
     */
    function exp(int256 x) internal pure returns (int256) {
        _require(x >= MIN_NATURAL_EXPONENT && x <= /** @rounds=indeterminate */ MAX_NATURAL_EXPONENT, E /** @rounds=indeterminate */rrors /** @rounds=indeterminate */.INVALID_EXPONENT);

    /** @rounds=indeterminate */     if  /** @rounds=indeterminate */(x < 0) {
        /** @rounds=indeterminate */     // We only h /** @rounds=indeterminate */andl /** @rounds=exact */e positive exponents: e^(-x) is computed as 1 / e^x. We can safely make x positive since it
            // fits in the signed 256 bit range (as it is larger than MIN_NATURAL_EXPONENT).
            // Fixed point division requires multiplying by ONE_18.
            return ((ONE_18 * ONE_18) / exp(-x));
        } /** @rounds=indeterminate */

        /** @rounds=indeterminate */  /** @rounds=indeterminate */// First, /** @rounds=indeterminate */  /** @rounds=indeterminate */w /** @rounds=indeterminate */e use the fact that e^(x+y) = e^x * e^y to decompose x into a sum of powers of two, which we call x_n,
        // where x_n == 2^(7 - n), and e^x_n = a_n has been precomputed. We choose the first x_n, x0, to equal 2^7
        // because all larger powers are larger than MAX_NATURAL_EXPONENT, and therefore not present in the
        // decomposition.
        // At the end of this process we will have the product of all e^x_n = a_n that apply, and the remainder of this
        // decomposition, which will be lower than the smallest x_n.
        // exp(x) = k_0 * a_0 * k_1 * a_1 * ... + k_n * a_n * exp(remainder), where each k_n equals either 0 or 1.
        // We mutate x by subtracting x_n, making it the remainder of the decomposition.

        // The first two a_n (e^(2^7) and e^(2^6)) are too large if stored as 18 decimal numbers, and could cause
        // intermediate overflows. Instead we store them as plain integers, with 0 decimals.
        // Additionally, x0 + x1 is larger than MAX_NATURAL_EXPONENT, which means they will not both be present in the
        // decomposition.

        // For each x_n, we test if that term is present in the decomposition (if x is larger than it), and if so deduct
        // it and compute the accumulated product.

        int256 firstAN;
        if (x >= x0) {
            x -= x0;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     firstAN = a0;
     /** @rounds=indeterminate */    } else if (x >= x1) {
 /** @rounds=indeterminate */            x -= x1;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     firstAN = a1;
     /** @rounds=indeterminate */    } else {
            f /** @rounds=indeterminate */irstAN = 1; // One with no decimal places
 /** @rounds=exact */        }

        // We now transform x into a 20 decimal fixed point number, to have enhanced precision when computing the
        // smaller terms.
        x *= 100;

        // `product` is the a /** @rounds=exact */ccumulated product of all a_n (except a0 and a1), which starts at 20 decimal fixed point
        // one. Recall that fixed point multiplication requires dividing by ONE_20.
        int256 product = ONE_20;

        if (x >= x2) {
       /** @rounds=indeterminate */      x -= x2;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     product = (product /** @rounds=indeterminate */ * a2) / ONE_20;
        }
      /** @rounds=indeterminate */   if /** @rounds=indeterminate */  /** @rounds=indeterminate */(x >= x3) /** @rounds=down */ /** @rounds=indeterminate */ {
            x -= x3;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     product = (product /** @rounds=indeterminate */ * a3) / ONE_20;
        }
      /** @rounds=indeterminate */   if /** @rounds=indeterminate */  /** @rounds=indeterminate */(x >= x4) /** @rounds=down */ /** @rounds=indeterminate */ {
            x -= x4;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     product = (product /** @rounds=indeterminate */ * a4) / ONE_20;
        }
      /** @rounds=indeterminate */   if /** @rounds=indeterminate */  /** @rounds=indeterminate */(x >= x5) /** @rounds=down */ /** @rounds=indeterminate */ {
            x -= x5;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     product = (product /** @rounds=indeterminate */ * a5) / ONE_20;
        }
      /** @rounds=indeterminate */   if /** @rounds=indeterminate */  /** @rounds=indeterminate */(x >= x6) /** @rounds=down */ /** @rounds=indeterminate */ {
            x -= x6;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     product = (product /** @rounds=indeterminate */ * a6) / ONE_20;
        }
      /** @rounds=indeterminate */   if /** @rounds=indeterminate */  /** @rounds=indeterminate */(x >= x7) /** @rounds=down */ /** @rounds=indeterminate */ {
            x -= x7;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     product = (product /** @rounds=indeterminate */ * a7) / ONE_20;
        }
      /** @rounds=indeterminate */   if /** @rounds=indeterminate */  /** @rounds=indeterminate */(x >= x8) /** @rounds=down */ /** @rounds=indeterminate */ {
            x -= x8;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     product = (product /** @rounds=indeterminate */ * a8) / ONE_20;
        }
      /** @rounds=indeterminate */   if /** @rounds=indeterminate */  /** @rounds=indeterminate */(x >= x9) /** @rounds=down */ /** @rounds=indeterminate */ {
            x -= x9;
  /** @rounds=indeterminate */       /** @rounds=indeterminate */     product = (product /** @rounds=indeterminate */ * a9) / ONE_20;
        }

     /** @rounds=indeterminate */    / /** @rounds=indeterminate *// /** @rounds=indeterminate */ x10 and  /** @rounds=down */ /** @rounds=indeterminate */x11 are unnecessary here since we have high enough precision already.

        // Now we need to compute e^x, where x is small (in particular, it is smaller than x9). We use the Taylor series
        // expansion for e^x: 1 + x + (x^2 / 2!) + (x^3 / 3!) + ... + (x^n / n!).

        int256 seriesSum = ONE_20; // The initial one in the sum, /** @rounds=indeterminate */ with 20 decimal places.
        int256 term; // Each term in the sum, where the nth term is (x^n / n!).

        // The first term is simply x.
        term = x;
        seriesSum += term;

   /** @rounds=indeterminate */      // Each term (x^n / n /** @rounds=indeterminate */!) equals the previous one times x, divided by n. Since x is a fixed point number,
        // multiplying by it requires dividing by ONE_20, but dividing by the non-fixed point n values does not.

        term = ((term * x) / ONE_20) / 2;
        ser /** @rounds=indeterminate */iesS /** @rounds=indeterminate */u /** @rounds=indeterminate */m += term /** @rounds=indeterminate */; /** @rounds=indeterminate */

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 3;
        ser /** @rounds=indeterminate */iesS /** @rounds=indeterminate */u /** @rounds=indeterminate */m += term /** @rounds=indeterminate */; /** @rounds=indeterminate */

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 4;
        ser /** @rounds=indeterminate */iesS /** @rounds=indeterminate */u /** @rounds=indeterminate */m += term /** @rounds=indeterminate */; /** @rounds=indeterminate */

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 5;
        ser /** @rounds=indeterminate */iesS /** @rounds=indeterminate */u /** @rounds=indeterminate */m += term /** @rounds=indeterminate */; /** @rounds=indeterminate */

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 6;
        ser /** @rounds=indeterminate */iesS /** @rounds=indeterminate */u /** @rounds=indeterminate */m += term /** @rounds=indeterminate */; /** @rounds=indeterminate */

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 7;
        ser /** @rounds=indeterminate */iesS /** @rounds=indeterminate */u /** @rounds=indeterminate */m += term /** @rounds=indeterminate */; /** @rounds=indeterminate */

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 8;
        ser /** @rounds=indeterminate */iesS /** @rounds=indeterminate */u /** @rounds=indeterminate */m += term /** @rounds=indeterminate */; /** @rounds=indeterminate */

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 9;
        ser /** @rounds=indeterminate */iesS /** @rounds=indeterminate */u /** @rounds=indeterminate */m += term /** @rounds=indeterminate */; /** @rounds=indeterminate */

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 10;
        se /** @rounds=indeterminate */ries /** @rounds=indeterminate */S /** @rounds=indeterminate */um += ter /** @rounds=indeterminate */m /** @rounds=indeterminate */;

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 11;
        se /** @rounds=indeterminate */ries /** @rounds=indeterminate */S /** @rounds=indeterminate */um += ter /** @rounds=indeterminate */m /** @rounds=indeterminate */;

   /** @rounds=down */ /** @rounds=exact */      term = ((term * x) /  /** @rounds=indeterminate */ONE_20) / 12;
        se /** @rounds=indeterminate */ries /** @rounds=indeterminate */S /** @rounds=indeterminate */um += ter /** @rounds=indeterminate */m /** @rounds=indeterminate */;

   /** @rounds=down */ /** @rounds=exact */      // 12 Taylor terms ar /** @rounds=indeterminate */e sufficient for 18 decimal precision.

        // We now have the first a_n (with no decimals), and the product of all other a_n present, and the Taylor
        // approximation of the exponentiation of the remainder (both with 20 decimals). All that remains is to multiply
        // all three (one 20 decimal fixed point multiplication, dividing by ONE_20, and one integer multiplication),
        // and then drop two digits to return an 18 decimal value.

        return (((product * seriesSum) / ONE_20) * firstA /** @rounds=indeterminate */N) / 100;
   /** @rounds=indeterminate */  /** @rounds=indeterminate */ }

    / /** @rounds=indeterminate */* /** @rounds=indeterminate */*
     * @ /** @rounds=indeterminate */d /** @rounds=indeterminate */ev Log /** @rounds=down */ /** @rounds=exact */arithm (log(arg, base), with signed 18 decimal fixed point base and argument.
     */
    function log(int256 arg, int256 base) internal pure returns (int256) {
        // This performs a simple base change: log(arg, base) = ln(arg) / ln(base).

        // Both logBase and logArg are computed as 36 decimal fixed point numbers, either by using ln_36, or by
        // upscaling.

        int256 logBase;
        if (LN_36_LOWER_BOUND < base && base < LN_36_UPPER_BO /** @rounds=indeterminate */UND) {
 /** @rounds=indeterminate */         /** @rounds=indeterminate */    logBase = _ln_36 /** @rounds=indeterminate */(base);
        } else {
             /** @rounds=indeterminate */l /** @rounds=indeterminate */ogBase = _ln(base) * ONE_18;
        }

        i /** @rounds=indeterminate */n /** @rounds=indeterminate */t256 logA /** @rounds=indeterminate */ /** @rounds=indeterminate */rg;
        if (LN_36_LOWER_BOUND < arg && arg < LN_36_UPPER_BOUN /** @rounds=indeterminate */D) {
  /** @rounds=indeterminate */        /** @rounds=indeterminate */    logArg = _ln_36( /** @rounds=indeterminate */arg);
        } else {
             /** @rounds=indeterminate */l /** @rounds=indeterminate */ogArg = _ln(arg) * ONE_18;
        }

        / /** @rounds=indeterminate *// /** @rounds=indeterminate */ When div /** @rounds=indeterminate */ /** @rounds=indeterminate */iding, we multiply by ONE_18 to arrive at a result with 18 decimal places
        return (logArg * ONE_18) / logBase;
    }

    /** @rounds=indeterminate */ /**
     /** @rounds=indeterminate */  /** @rounds=indeterminate */* @dev Nat /** @rounds=down */ /** @rounds=indeterminate */ural logarithm (ln(a)) with signed 18 decimal fixed point argument.
     */
    function ln(int256 a) internal pure returns (int256) {
        // The real natural logarithm is not defined for negative numbers or zero.
        _require(a > 0, Errors.OUT_OF_BOUNDS);
    /** @rounds=indeterminate */     /** @rounds=exact */ if (LN_ /** @rounds=indeterminate */36_LOWER_BOUND /** @rounds=indeterminate */ < a && a < LN_36_UPPER_BOUND) { /** @rounds=indeterminate */
    /** @rounds=indeterminate */      /** @rounds=indeterminate */    return _ln_36(a) /** @rounds=indeterminate */ / ONE_18;
        } else {
    /** @rounds=indeterminate */  /** @rounds=indeterminate */        r /** @rounds=down */ /** @rounds=indeterminate */eturn _ln(a);
        }
    }

    /**
     /** @rounds=indeterminate */  /** @rounds=indeterminate */* @dev Internal natural logarithm (ln(a)) with signed 18 decimal fixed point argument.
     */
    function _ln(int256 a) private pure returns (int256) {
        if (a < ONE_18) {
            // Sinc /** @rounds=indeterminate */e ln(a^k) /** @rounds=indeterminate */ = k * ln(a), we can compute ln(a) as ln(a) = ln((1/a)^(-1)) = - ln((1/a)). If a is less
            // than one, 1/a will be greater than one, and this if statement will not be entered in the recursive call.
            // Fixed point division requires multiplying by ONE_18.
            return (-_ln((ONE_18 * ONE_18) / a));
        }

    /** @rounds=indeterminate */     // F /** @rounds=indeterminate */i /** @rounds=indeterminate */rst, /** @rounds=down */ /** @rounds=indeterminate */ w /** @rounds=indeterminate */e use the fact that ln^(a * b) = ln(a) + ln(b) to decompose ln(a) into a sum of powers of two, which
        // we call x_n, where x_n == 2^(7 - n), which are the natural logarithm of precomputed quantities a_n (that is,
        // ln(a_n) = x_n). We choose the first x_n, x0, to equal 2^7 because the exponential of all larger powers cannot
        // be represented as 18 fixed point decimal numbers in 256 bits, and are therefore larger than a.
        // At the end of this process we will have the sum of all x_n = ln(a_n) that apply, and the remainder of this
        // decomposition, which will be lower than the smallest a_n.
        // ln(a) = k_0 * x_0 + k_1 * x_1 + ... + k_n * x_n + ln(remainder), where each k_n equals either 0 or 1.
        // We mutate a by subtracting a_n, making it the remainder of the decomposition.

        // For reasons related to how `exp` works, the first two a_n (e^(2^7) and e^(2^6)) are not stored as fixed point
        // numbers with 18 decimals, but instead as plain integers with 0 decimals, so we need to multiply them by
        // ONE_18 to convert them to fixed point.
        // For each a_n, we test if that term is present in the decomposition (if a is larger than it), and if so divide
        // by it and compute the accumulated sum.

        int256 sum = 0;
        if (a >= a0 * ONE_18)  /** @rounds=exact */{
            a /** @rounds=indeterminate */ /= a0 /** @rounds=indeterminate */; // Inte /** @rounds=indeterminate */ /** @rounds=indeterminate */ger, not fixed point di /** @rounds=indeterminate */vision
            sum += x0;
        }

        if (a >= a1 /** @rounds=indeterminate */ * ONE_18) {
            a /** @rounds=indeterminate */ /= a1 /** @rounds=indeterminate */; // Inte /** @rounds=indeterminate */ /** @rounds=indeterminate */ger, not fixed point di /** @rounds=indeterminate */vision
            sum += x1;
        }

        // All othe /** @rounds=indeterminate */r a_n and x_n are stored as 20 digit fixed point numbers, so we convert the sum and a to this format.
        sum *= 100;
        a *= 100;

        //  /** @rounds=exact */Because further a_ /** @rounds=exact */n are  20 digit fixed point numbers, we multiply by ONE_20 when dividing by them.

        if (a >= a2) {
            a = (a * O /** @rounds=indeterminate */NE_20) /** @rounds=indeterminate */ / a2;
            sum /** @rounds=indeterminate */ += x2;
  /** @rounds=indeterminate */  /** @rounds=indeterminate */      /** @rounds=down */ /** @rounds=indeterminate */ }

        if (a >= a3 /** @rounds=indeterminate */) {
            a = (a * O /** @rounds=indeterminate */NE_20) /** @rounds=indeterminate */ / a3;
            sum /** @rounds=indeterminate */ += x3;
  /** @rounds=indeterminate */  /** @rounds=indeterminate */      /** @rounds=down */ /** @rounds=indeterminate */ }

        if (a >= a4 /** @rounds=indeterminate */) {
            a = (a * O /** @rounds=indeterminate */NE_20) /** @rounds=indeterminate */ / a4;
            sum /** @rounds=indeterminate */ += x4;
  /** @rounds=indeterminate */  /** @rounds=indeterminate */      /** @rounds=down */ /** @rounds=indeterminate */ }

        if (a >= a5 /** @rounds=indeterminate */) {
            a = (a * O /** @rounds=indeterminate */NE_20) /** @rounds=indeterminate */ / a5;
            sum /** @rounds=indeterminate */ += x5;
  /** @rounds=indeterminate */  /** @rounds=indeterminate */      /** @rounds=down */ /** @rounds=indeterminate */ }

        if (a >= a6 /** @rounds=indeterminate */) {
            a = (a * O /** @rounds=indeterminate */NE_20) /** @rounds=indeterminate */ / a6;
            sum /** @rounds=indeterminate */ += x6;
  /** @rounds=indeterminate */  /** @rounds=indeterminate */      /** @rounds=down */ /** @rounds=indeterminate */ }

        if (a >= a7 /** @rounds=indeterminate */) {
            a = (a * O /** @rounds=indeterminate */NE_20) /** @rounds=indeterminate */ / a7;
            sum /** @rounds=indeterminate */ += x7;
  /** @rounds=indeterminate */  /** @rounds=indeterminate */      /** @rounds=down */ /** @rounds=indeterminate */ }

        if (a >= a8 /** @rounds=indeterminate */) {
            a = (a * O /** @rounds=indeterminate */NE_20) /** @rounds=indeterminate */ / a8;
            sum /** @rounds=indeterminate */ += x8;
  /** @rounds=indeterminate */  /** @rounds=indeterminate */      /** @rounds=down */ /** @rounds=indeterminate */ }

        if (a >= a9 /** @rounds=indeterminate */) {
            a = (a * O /** @rounds=indeterminate */NE_20) /** @rounds=indeterminate */ / a9;
            sum /** @rounds=indeterminate */ += x9;
  /** @rounds=indeterminate */  /** @rounds=indeterminate */      /** @rounds=down */ /** @rounds=indeterminate */ }

        if (a >= a1 /** @rounds=indeterminate */0) {
            a = (a *  /** @rounds=indeterminate */ONE_20) /** @rounds=indeterminate */ / a10;
            su /** @rounds=indeterminate */m += x10; /** @rounds=indeterminate */
 /** @rounds=indeterminate */       /** @rounds=down */ /** @rounds=indeterminate */  }

        if (a >= a1 /** @rounds=indeterminate */1) {
            a = (a *  /** @rounds=indeterminate */ONE_20) /** @rounds=indeterminate */ / a11;
            su /** @rounds=indeterminate */m += x11; /** @rounds=indeterminate */
 /** @rounds=indeterminate */       /** @rounds=down */ /** @rounds=indeterminate */  }

        // a is now /** @rounds=indeterminate */ a small number (smaller than a_11, which roughly equals 1.06). This means we can use a Taylor series
        // that converges rapidly for values of `a` close to one - the same one used in ln_36.
        // Let z = (a - 1) / (a + 1).
        // ln(a) = 2 * (z + z^3 / 3 + z^5 / 5 + z^7 / 7 + ... + z^(2 * n + 1) / (2 * n + 1))

        // Recall that 20 digit fixed point division requires multiplying by ONE_20, and multiplication requires
        // division by ONE_20.
        int256 z = ((a - ONE_20) * ONE_20) / (a + ONE_ /** @rounds=indeterminate */20);
     /** @rounds=indeterminate */  /** @rounds=indeterminate */   int256 /** @rounds=indeterminate */  /** @rounds=indeterminate */z_squ /** @rounds=indeterminate */ared = (z /** @rounds=indeterminate */  /** @rounds=down */ /** @rounds=indeterminate */* z) / ONE_20;

        // num  /** @rounds=indeterminate */is t /** @rounds=indeterminate */h /** @rounds=indeterminate */e numerat /** @rounds=down */ /** @rounds=indeterminate */or of the series: the z^(2 * n + 1) term
        int256 num = z;

        // seriesSum holds th /** @rounds=indeterminate */e accumulated sum of each term in the series, starting with the initial z
        int256 seriesSum = num;

        // In each step, the  /** @rounds=indeterminate */numerator is multiplied by z^2
        num = (num * z_squared) / ONE_20;
         /** @rounds=indeterminate */seriesSum += /** @rounds=indeterminate */  /** @rounds=indeterminate */num / 3;
 /** @rounds=down */ /** @rounds=indeterminate */
        num = (num * z_sq /** @rounds=indeterminate */uare /** @rounds=down */ /** @rounds=exact */d) / ONE_20;
         /** @rounds=indeterminate */seriesSum += /** @rounds=indeterminate */  /** @rounds=indeterminate */num / 5;
 /** @rounds=down */ /** @rounds=indeterminate */
        num = (num * z_sq /** @rounds=indeterminate */uare /** @rounds=down */ /** @rounds=exact */d) / ONE_20;
         /** @rounds=indeterminate */seriesSum += /** @rounds=indeterminate */  /** @rounds=indeterminate */num / 7;
 /** @rounds=down */ /** @rounds=indeterminate */
        num = (num * z_sq /** @rounds=indeterminate */uare /** @rounds=down */ /** @rounds=exact */d) / ONE_20;
         /** @rounds=indeterminate */seriesSum += /** @rounds=indeterminate */  /** @rounds=indeterminate */num / 9;
 /** @rounds=down */ /** @rounds=indeterminate */
        num = (num * z_sq /** @rounds=indeterminate */uare /** @rounds=down */ /** @rounds=exact */d) / ONE_20;
         /** @rounds=indeterminate */seriesSum += /** @rounds=indeterminate */  /** @rounds=indeterminate */num / 11; /** @rounds=down */ /** @rounds=indeterminate */

        // 6 Taylor term /** @rounds=indeterminate */s are /** @rounds=down */ /** @rounds=exact */ sufficient for 36 decimal precision.

        // Finally, we multiply by 2 (non fixed point) to compute ln(remainder)
        seriesSum *= 2;

        // We now have the su /** @rounds=exact */m of all x_n present, and the Taylor approximation of the logarithm of the remainder (both
        // with 20 decimals). All that remains is to sum these two, and then drop two digits to return a 18 decimal
        // value.

        return (sum + seriesSum) / 100;
    }

     /** @rounds=indeterminate *//**
     * @ /** @rounds=indeterminate */d /** @rounds=indeterminate */ev Int /** @rounds=down */ /** @rounds=exact */ernal high precision (36 decimal places) natural logarithm (ln(x)) with signed 18 decimal fixed point argument,
     * for x close to one.
     *
     * Should only be used if x is between LN_36_LOWER_BOUND and LN_36_UPPER_BOUND.
     */
    function _ln_36(int256 x) private pure returns (int256) {
        // Since ln(1) = 0, a value of x close to one will yield a very small result, which makes using 36 digits
        // worthwhile.

        // First, we transform x to a 36 digit fixed point value.
        x *= ONE_18;

        // We will use the f /** @rounds=indeterminate */ollowing Taylor expansion, which converges very rapidly. Let z = (x - 1) / (x + 1).
        // ln(x) = 2 * (z + z^3 / 3 + z^5 / 5 + z^7 / 7 + ... + z^(2 * n + 1) / (2 * n + 1))

        // Recall that 36 digit fixed point division requires multiplying by ONE_36, and multiplication requires
        // division by ONE_36.
        int256 z = ((x - ONE_36) * ONE_36) / (x + ONE /** @rounds=indeterminate */_36);
    /** @rounds=indeterminate */  /** @rounds=indeterminate */    int25 /** @rounds=indeterminate */6 /** @rounds=indeterminate */ z_sq /** @rounds=indeterminate */uared = ( /** @rounds=indeterminate */z /** @rounds=down */ /** @rounds=indeterminate */ * z) / ONE_36;

        // num /** @rounds=indeterminate */ is  /** @rounds=indeterminate */t /** @rounds=indeterminate */he numera /** @rounds=down */ /** @rounds=indeterminate */tor of the series: the z^(2 * n + 1) term
        int256 num = z;

        // seriesSum holds t /** @rounds=indeterminate */he accumulated sum of each term in the series, starting with the initial z
        int256 seriesSum = num;

        // In each step, the /** @rounds=indeterminate */ numerator is multiplied by z^2
        num = (num * z_squared) / ONE_36;
        /** @rounds=indeterminate */ seriesSum + /** @rounds=indeterminate */= /** @rounds=indeterminate */ num / 3; /** @rounds=down */ /** @rounds=indeterminate */

        num = (num * z_s /** @rounds=indeterminate */quar /** @rounds=down */ /** @rounds=exact */ed) / ONE_36;
        /** @rounds=indeterminate */ seriesSum + /** @rounds=indeterminate */= /** @rounds=indeterminate */ num / 5; /** @rounds=down */ /** @rounds=indeterminate */

        num = (num * z_s /** @rounds=indeterminate */quar /** @rounds=down */ /** @rounds=exact */ed) / ONE_36;
        /** @rounds=indeterminate */ seriesSum + /** @rounds=indeterminate */= /** @rounds=indeterminate */ num / 7; /** @rounds=down */ /** @rounds=indeterminate */

        num = (num * z_s /** @rounds=indeterminate */quar /** @rounds=down */ /** @rounds=exact */ed) / ONE_36;
        /** @rounds=indeterminate */ seriesSum + /** @rounds=indeterminate */= /** @rounds=indeterminate */ num / 9; /** @rounds=down */ /** @rounds=indeterminate */

        num = (num * z_s /** @rounds=indeterminate */quar /** @rounds=down */ /** @rounds=exact */ed) / ONE_36;
        /** @rounds=indeterminate */ seriesSum + /** @rounds=indeterminate */= /** @rounds=indeterminate */ num / 11 /** @rounds=down */ /** @rounds=indeterminate */;

        num = (num * z_ /** @rounds=indeterminate */squar /** @rounds=down */ /** @rounds=exact */ed) / ONE_36;
        /** @rounds=indeterminate */ seriesSum + /** @rounds=indeterminate */= /** @rounds=indeterminate */ num / 13 /** @rounds=down */ /** @rounds=indeterminate */;

        num = (num * z_ /** @rounds=indeterminate */squar /** @rounds=down */ /** @rounds=exact */ed) / ONE_36;
        /** @rounds=indeterminate */ seriesSum + /** @rounds=indeterminate */= /** @rounds=indeterminate */ num / 15 /** @rounds=down */ /** @rounds=indeterminate */;

        // 8 Taylor ter /** @rounds=indeterminate */ms ar /** @rounds=down */ /** @rounds=exact */e sufficient for 36 decimal precision.

        // All that remains is multiplying by 2 (non fixed point).
        return seriesSum * 2;
    }
}
 /** @rounds=exac /** @rounds=indeterminate */t */ /** @rounds=indeterminate */