# Age Verification Methods Demo

Streamlit app hosted at [ageverify.streamlit.app](https://ageverify.streamlit.app/), with a GitHub pages redirect live from [age.oryley.com](https://age.oryley.com/).

Created for the **UK Parliament Hackathon** hosted at the House of Lords on the 4th September 2026, organised by EasyA.

## Australia's Current Solution

Australia passed the *Online Safety Amendment (Social Media Minimum Age) Act* in late 2024, which implements a strict under-16s social media ban, which took full effect on 10 December 2025 [1]. 

Rather than enforcing a "one size fits all" solution, the Australia has a framework that expects platforms to use "successive validation" [2]. This typically begins with age inference signals (e.g., IP geolocation, device history). If a user is suspected of being underage, platforms escalate to stronger checks, such as facial age estimation and document-based verification [2][3]. A recent $6.5m government-backed trial testing 60 different technologies across 48 vendors emphasized that multiple "fallback options" are legally required when primary estimation methods fail [4].

## Ofcom Methods Demonstrated Here

According to Ofcom's official guidance [5], the primary recognized methods for age verification are:

* **Facial age estimation**
  * Ofcom method: You show your face via photo or video, and technology analyses it to estimate your age.
  * Demonstrated here: Captures a live webcam image and runs local computer-vision inference with DeepFace.
* **Open banking**
  * Ofcom method: You give permission for an age-check service to access confirmation from your bank about whether you are over 18.
  * Demonstrated here: Mocks consent, a scoped `age_over_18` request, and a bank callback containing a request ID and threshold result.
* **Digital identity services**
  * Ofcom method: A digital identity wallet securely stores and shares information that proves your age.
  * Demonstrated here: Generates and verifies a signed selective-disclosure claim without sharing a date of birth.
* **Credit card age checks**
  * Ofcom method: A payment processor checks whether a provided card is valid; obtaining a credit card indicates the holder is over 18.
  * Demonstrated here: Simulates a tokenized processor response using only a card network and last four digits.
* **Email-based age estimation**
  * Ofcom method: A service analyses other online services linked to your email address to estimate your age.
  * Demonstrated here: Mocks a signals-provider response with account history, an age band, confidence, and a request ID.
* **Mobile network operator age checks**
  * Ofcom method: With permission, an age-check service confirms whether age filters are applied to your mobile number.
  * Demonstrated here: Mocks a consented operator lookup returning an age-filter result and lookup ID.
* **Photo-ID matching**
  * Ofcom method: An image of an identity document and a selfie are compared to confirm that the document belongs to you.
  * Demonstrated here: Parses the document MRZ and computes exact age, then provides the selfie and document inputs for a production face-embedding comparison.

## Citations

1. Wikipedia (2026). *Online Safety Amendment (Social Media Minimum Age) Act 2024*. Available at: https://en.wikipedia.org/wiki/Online_Safety_Amendment_(Social_Media_Minimum_Age)_Act_2024
2. IEEE Standards Association (2026). *The Australian Social Media Ban & Age Verification — What Does it Mean for Your Global App?* Available at: https://standards.ieee.org/beyond-standards/the-australian-social-media-ban-age-verification/
3. eSafety Commissioner (Australia) (2026). *Social media age restrictions*. Available at: https://www.esafety.gov.au/industry/tech-trends-and-challenges/social-media-age-restrictions
4. The Guardian (2025). *Trial of tech that could be used to keep Australian under-16s off social media finds some errors 'inevitable'*. 
5. Ofcom. *Age checks for online safety – what you need to know as a user*. Available at: https://www.ofcom.org.uk/online-safety/protecting-children/age-checks-for-online-safety--what-you-need-to-know-as-a-user

## BibTeX Citation for this Repo

```bibtex
@misc{ryley_2026_ageverify,
  author       = {Ryley, Oscar},
  title        = {Age Verification Methods Demo},
  year         = {2026},
  publisher    = {GitHub},
  journal      = {GitHub Repository},
  howpublished = {\url{https://github.com/oscar-ryley/age-verification}},
  note         = {Created for the UK Parliament Hackathon hosted at the House of Lords, organised by EasyA}
}
```
