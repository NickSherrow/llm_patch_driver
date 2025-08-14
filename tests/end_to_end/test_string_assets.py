
TEST_STRING_PROMPT = """
Generate a template for employee agreement.

Requirements:
- The agreement should be exactly {TEXT_LENGTH} words. Not longer, not shorter. The words counter will be performed using len(text.split()) in Python.
- The agreement must include the following sections: {SECTIONS}. Only these sections are allowed. No other sections are allowed. All these sections must be present.
- This agreement must include {WEIRD_CONDITION}
- Do not return any other text than the agreement. Start your response with "EMPLOYMENT AGREEMENT" and end with "EXHIBIT A".
"""

WEIRD_CONDITION = """limitations that prevent the employer from hiring anyone who might work on similar projects as the employee. Employee is the only person in the company who is allowed to work on projects."""

TEXT_LENGTH = 3000

SECTIONS = [
    "Duties and Scope of Employment", 
    "Cash and Incentive Compensation", 
    "Business Expenses", 
    "Term of Employment",
    "Supervision",
    "Termination Benefits", 
    "Invention, Confidential Information and Non-Competition Agreement", 
    "Miscellaneous Provisions"]

DOC = """
EMPLOYMENT AGREEMENT
This Employment Agreement (the “Agreement”) is effective as of January 6, 2004
(the “Effective Date”) by and between John O'Keefe (the “Executive”) and Verdisys, Inc., a
California corporation (the “Company”).
1. Duties and Scope of Employment.
(a) Position. For the term of this Agreement, the Company agrees to employ
the Executive in the position of Executive Vice President and Chief Financial Officer (the
“Employment”). The duties and responsibilities of Executive shall include the duties and
responsibilities for the Executive's corporate office and position as set forth in the
Company's bylaws and such other duties and responsibilities as the Company's Chief
Executive Officer and/or Board of Directors may from time to time reasonably assign to
the Executive.
(b) Obligations to the Company. During his Employment, the Executive
shall devote his full business efforts and time to the Company. During his Employment,
without prior written approval from the Company's Chief Executive Officer, the
Executive shall not render services in any capacity to any other person or entity and shall
not act as a sole proprietor or partner of any other person or entity or as a shareholder or
other owner owning more than ten percent of the stock or other interests of any other
corporation or entity. This obligation, however, shall not preclude Executive from
engaging in appropriate civic, charitable or religious activities or from devoting a
reasonable amount of time to private investments or from serving on the boards of
directors of companies, including closely held companies which are controlled by
Executive as long as these activities or services do not materially interfere or conflict
with Executive's responsibilities to, or ability to perform his duties of employment by,
the Company under this Agreement. The Executive shall comply with the Company's
policies and rules as they may be in effect from time to time during his Employment.
(c) No Conflicting Obligations. The Executive represents and warrants to
the Company that he is under no obligations or commitments, whether contractual or
otherwise, that are inconsistent with his obligations under this Agreement. The Executive
represents and warrants that he will not use or disclose, in connection with his
employment by the Company, any trade secrets or other proprietary information or
intellectual property in which the Executive or any other person has any right, title or
interest and that his employment by the Company as contemplated by this Agreement
will not infringe or violate the rights of any other person. The Executive represents and
warrants to the Company that he has returned all property and confidential information
belonging to any prior employer. 
2. Cash and Incentive Compensation.
(a) Salary. The Company shall pay the Executive as compensation for his
services during the first twelve (12) months of his Employment a base salary at a gross
annual rate of $175,000. Such salary shall be payable in accordance with the Company's
standard payroll procedures. Only in the event that the parties extend the term of this
Agreement pursuant to Section 4(a), then Company shall pay the Executive as
compensation for his service during the second twelve (12) months of his Employment a
base salary at a gross annual rate of $195,000 and, if applicable, for his service during the
third twelve (12) months of his Employment a base salary at a gross annual rate of
$215,000. (The annual compensation specified in this Subsection (a), together with any
increases in such compensation as a result of an extension of the term of this Agreement
pursuant to Section 4(a), is referred to in this Agreement as “Base Compensation.”)
(b) Bonus. Executive shall receive a one time payment of $40,000 as a sign
on bonus and shall be included in the Company Executive Compensation program,
whereby senior management are eligible to receive annual bonuses of up to 50% of their
base compensation.
(c) Options. Executive shall be eligible to be considered for stock option
grants under the Company's annual stock option award program as administered by, and
at the discretion of, the Compensation Committee of the Board of Directors. An initial
option shall be granted to the Executive for the right to purchase an aggregate of 80,000
shares of the Company's common stock at an exercise price based upon the date of
approval by the Compensation Committee of the Board of Directors. Such option shall
vest quarterly over the initial term of this Agreement.
(d) Insurance Coverage Reimbursement. Company agrees to pay Executive
at current rate of $394 per month to cover and to be in lieu of medical benefits, as
selected by Executive in his sole discretion. Executive understands and agrees that
Company is not required to permit Executive to participate in any Company-sponsored
benefit plans, including but not limited to the Company's medical plan, in the same or
any manner as Company and any third-party benefit provider make such opportunities
available to Company's regular full-time employees; provided, however, if Company
does provide such Company-sponsored benefit plans and Executive is eligible to
participate in such Company-sponsored benefit plans, Executive shall not be entitled to
receive such $394 monthly payment.
(e) Vacation. During the term of this Agreement, Executive shall be entitled
to vacation each year in accordance with the Company's policies in effect from time to
time, but in no event less than four (4) weeks paid vacation per calendar year.
3. Business Expenses. During his Employment, the Executive shall be
authorized to incur necessary and reasonable travel, entertainment and other business
expenses in connection with his duties hereunder. The Company shall reimburse the
Executive for such expenses upon presentation of an itemized account and appropriate
supporting documentation, all in accordance with the Company's generally applicable
2 
policies. The Executive shall have a car allowance of $1,000.00 per month during the
term of this Agreement.
4. Term of Employment.
(a) Term. This Agreement shall expire on the first anniversary of the
Effective Date, unless otherwise extended by the mutual agreement of Executive and the
Company; provided, that this Agreement shall automatically be renewed for additional
one (1) year terms and shall automatically be continued effective as of the subsequent
anniversary date of the Agreement (a “Renewal Date”) unless the Company or Executive
has delivered written notice of non-renewal to the other party at least sixty (60) days prior
to the relevant Renewal Date.
(b) Basic Rule. The Executive's Employment with the Company shall be “at
will,” meaning that either the Executive or the Company shall be entitled to terminate the
Executive's Employment at any time and for any reason, with or without Cause (in the
case of the Company) or Constructive Termination (in the case of Executive). Any
contrary representations that may have been made to the Executive shall be superseded
by this Agreement. This Agreement shall constitute the full and complete agreement
between the Executive and the Company on the “at will” nature of the Executive's
Employment, which may be changed only in an express written agreement signed by the
Executive and a duly authorized officer of the Company.
(c) Termination. The Company or the Executive may terminate the
Executive's Employment at any time and for any reason (or no reason), and with or
without Cause (in the case of the Company) or Constructive Termination (in the case of
Executive), by giving the other party notice in writing. The Executive's Employment
shall terminate automatically in the event of his death.
(d) Rights Upon Termination. Except as expressly provided in Section 5,
upon the termination of the Executive's Employment pursuant to this Section 4, the
Executive shall be entitled only to the compensation, benefits and reimbursements
described in Sections 2 and 3 for the period preceding the effective date of the
termination.
5. Termination Benefits.
(a) General Release. Any other provision of this Agreement
notwithstanding, Subsections (b), (c), and (d) below shall not apply unless the Employee
(i) has executed a general release (in a form reasonably prescribed by the Company) of
all known and unknown claims that he may then have against the Company or persons
affiliated with the Company, and (ii) has agreed not to prosecute any legal action or other
proceeding based upon any of such claims.
(b) Severance Pay. If, during the term of this Agreement, the Company
terminates the Executive's Employment for any reason other than Cause or Disability, or
if the Executive voluntarily resigns following a Constructive Termination, (collectively, a
“Termination Event”), then the Company shall pay the Executive his Base Compensation
3 
for the remaining period of the then-current term of this Agreement, but not in excess of
six (6) months. Such Base Compensation shall be paid as a lump sum within thirty (30)
days after the Termination Event. In addition, the Company shall also reimburse the
Executive for the payment of the Executive's COBRA or equivalent other replacement
medical and dental insurance premiums for a period of six (6) months.
(c) Stock Options. With respect to all stock options in the Company granted
to Executive prior to the effective date of the Termination Event, an amount of option
shares equal to the number of months for which Executive is entitled to receive severance
pay will become immediately vested, not subject to repurchase and not subject to
assumption, assignment or replacement by the Company or its successors.
(d) Disability. If the Executive's employment is terminated by the Company
by reason of the Executive's Disability, the Executive shall be entitled to a prompt cash
payment of a prorated portion of the payments set forth in Section 2(a) above for the year
in which such termination occurs. Executive and his eligible dependents shall be entitled
to continued participation so long as he is disabled and is not eligible for coverage under
a successor employer's plans through the month in which the Executive attains age sixtyfive (65) in all medical, dental, vision and hospitalization insurance coverage, and in all
other employee welfare benefit plans, programs and arrangements in which he was
participating on the date of termination of his employment for Disability on terms and
conditions that are no less favorable than those applicable, from time to time, to senior
executives of the Company. For purposes of this Agreement, “Disability” means the
Executive's inability, due to physical or mental incapacity, to substantially perform his
duties and responsibilities contemplated by this Agreement. In the event of a dispute as to
whether the Executive is disabled, the determination shall be made by a licensed medical
doctor selected by the Company and agreed to by the Executive. If the parties cannot
agree on a medical doctor, each party shall select a medical doctor and the two doctors
shall select a third who shall be the approved medical doctor for this purpose. The
Executive agrees to submit to such tests and examinations as such medical doctor shall
deem appropriate.
(e) Definition of “Cause.” For all purposes under this Agreement, “Cause”
shall mean:
(i) Any breach of the Invention, Confidential Information and NonCompetition Agreement referenced in Section 6 hereof between the Executive
and the Company, as determined by the Board of Directors of the Company;
(ii) Conviction of, or a plea of “guilty” or “no contest” to, a felony, or
a plea of “guilty” or “no contest” to a lesser included offense in exchange for
withdrawal of a felony indictment or felony charge by indictment, in each case
whether arising under the laws of the United States or any state thereof;
(iii) Any act or acts of fraud;
(iv) violations of applicable laws, rules or regulations that expose the
4 
Company to material damages or material liability
(v) material breach by the employee of any material provision of the
Employment Agreement that remains uncorrected for 30 days following written
notice of such breach to the employee by the company.
(f) Definition of “Constructive Termination.” For all purposes under this
Agreement, Constructive Termination shall mean the voluntary resignation of the
Executive within 60 days following:
(i) The failure of the Executive to be elected or reelected to any of
the positions described in Section 1(a) or his removal from any such position
without his written consent.
(ii) A material diminution in the Executive's duties or the assignment
of him of any duties inconsistent with the Executive's position and status as
Executive Vice President and Chief Financial Officer of the Company.
(iii) A change in the Executive's reporting relationship such that the
Executive no longer reports directly to the Chief Executive Officer.
(iv) A reduction in the Executive's Base Compensation without his
consent;
(v) Receipt of notice from Company that the Executive's principal
workplace will be relocated by more than fifty (50) miles without his written
consent;
(vi) A breach by the Company of any of its material obligations to the
Executive under this Agreement; or
(vii) The failure of the Company to obtain a satisfactory agreement
from any successor to all or substantially all of the assets or business of the
Company to assume and agree to perform this Agreement within 15 days after a
merger, consolidation, sale or similar transaction.
6. Invention, Confidential Information and Non-Competition
Agreement. The Executive has entered into an Invention, Confidential
Information and Non-Competition Agreement with the Company, in the form
attached hereto as Exhibit A, which is incorporated herein by reference.
7. Successors.
(a) Company's Successors. This Agreement shall be binding upon
any successor (whether direct or indirect and whether by purchase, lease, merger,
consolidation, liquidation or otherwise) to all or substantially all of the Company's
business and/or assets. For all purposes under this Agreement, the term
5 
“Company” shall include any successor to the Company's business and/or assets
which becomes bound by this Agreement.
(b) Executive's Successors. This Agreement and all rights of the Executive
hereunder shall inure to the benefit of, and be enforceable by, the Executive's personal or
legal representatives, executors, administrators, successors, heirs, distributees, devisees
and legatees.
8. Miscellaneous Provisions.
(a) Notice. Notices and all other communications contemplated by this
Agreement shall be in writing and shall be deemed to have been duly given when
personally delivered or when mailed by U.S. registered or certified mail, return receipt
requested and postage prepaid. In the case of the Executive, mailed notices shall be
addressed to him at the home address which he most recently communicated to the
Company in writing. In the case of the Company, mailed notices shall be addressed to its
corporate headquarters, and all notices shall be directed to the attention of its Secretary.
(b) Modifications and Waivers. No provision of this Agreement shall be
modified, waived or discharged unless the modification, waiver or discharge is agreed to
in writing and signed by the Executive and by an authorized officer of the Company
(other than the Executive). No waiver by either party of any breach of, or of compliance
with, any condition or provision of this Agreement by the other party shall be considered
a waiver of any other condition or provision or of the same condition or provision at
another time.
(c) Indemnification. To the fullest extent permitted by the
indemnification provisions of the Articles of Incorporation and Bylaws of the Company
in effect as of the date of this Agreement, and the indemnification provision of the laws
of the jurisdiction of the Company's incorporation in effect from time to time, the
Company shall indemnify the Executive as a director, senior officer or employee of the
Company against all liabilities and reasonable expenses that may be incurred in any
threatened, pending or completed action, suit or proceeding, and shall pay for the
reasonable expenses incurred by the Executive in the defense of or participation in any
proceeding to which the Executive is a party because of his service to the Company. The
rights of the Executive under this indemnification provision shall survive the termination
of employment.
(d) Whole Agreement. This Agreement and the Invention, Confidential
Information and Non-Competition Agreement between the Company and Executive
contain the entire understanding of the parties with respect to the subject matter hereof.
No other agreements, representations or understandings (whether oral or written and
whether express or implied) which are not expressly set forth in such agreements have
been made or entered into by either party with respect to the subject matter hereof.
(e) Withholding Taxes. All payments made under this Agreement shall be
subject to reduction to reflect taxes or other charges required to be withheld by law.
6 
(f) Choice of Law and Severability. This Agreement is executed by the
parties in the State of Texas and shall be interpreted in accordance with the laws of such
State (except their provisions governing the choice of law). If any provision of this
Agreement becomes or is deemed invalid, illegal or unenforceable in any jurisdiction by
reason of the scope, extent or duration of its coverage, then such provision shall be
deemed amended to the extent necessary to conform to applicable law so as to be valid
and enforceable or, if such provision cannot be so amended without materially altering
the intention of the parties, then such provision shall be stricken and the remainder of this
Agreement shall continue in full force and effect. Should there ever occur any conflict
between any provision contained in this Agreement and any present or future statute, law,
ordinance or regulation contrary to which the parties have no legal right to contract, then
the latter shall prevail but the provision of this Agreement affected thereby shall be
curtailed and limited only to the extent necessary to bring it into compliance with
applicable law. All the other terms and provisions of this Agreement shall continue in
full force and effect without impairment or limitation.
(g) Arbitration. Any controversy or claim arising out of or relating to this
Agreement or the breach thereof, or the Executive's Employment or the termination
thereof, shall be settled in Houston, Texas, by arbitration in accordance with the National
Rules for the Resolution of Employment Disputes of the American Arbitration
Association. The decision of the arbitrator shall be final and binding on the parties, and
judgment on the award rendered by the arbitrator may be entered in any court having
jurisdiction thereof. The parties hereby agree that the arbitrator shall be empowered to
enter an equitable decree mandating specific enforcement of the terms of this Agreement.
The Company and the Executive shall share equally all fees and expenses of the
arbitrator. The Executive hereby consents to personal jurisdiction of the state and federal
courts located in the State of Texas for any action or proceeding arising from or relating
to this Agreement or relating to any arbitration in which the parties are participants.
(h) No Assignment. This Agreement and all rights and obligations of the
Executive hereunder are personal to the Executive and may not be transferred or assigned
by the Executive at any time. The Company may assign its rights under this Agreement
to any entity that assumes the Company's obligations hereunder in connection with any
sale or transfer of all or a substantial portion of the Company's assets to such entity.
(i) Counterparts. This Agreement may be executed in two or more
counterparts, each of which shall be deemed an original, but all of which together shall
constitute one and the same instrument.
[SIGNATURE PAGE FOLLOWS]
7 
IN WITNESS WHEREOF, each of the parties has executed this Agreement, in the case of the
Company by its duly authorized officer, as of the day and year first above written.
/s/ John O'Keefe
 JOHN O'KEEFE
 VERDISYS, INC.
By: /s/ Dr. Ron Robinson
Name: Dr. Ron Robinson
Title: Chairman
8 
EXHIBIT A
"""

REFLECTION_PROMPT = """
# TASK AND INSTRUCTIONS

Your job is to check wether the document complies with a set of rules.

## THE DOCUMENT

<context>
The document is an employment agreement template.
</context>

<document>
{DOCUMENT}
</document>

## THE RULES

<rule_1>
The document must include only the following sections: {SECTIONS}.

If you see any other sections, you must report them. If any sections are missing, you must report them.
</rule_1>

<rule_2>
The document must include the following condition: {WEIRD_CONDITION}.

If the condition is not present, you must report it.
</rule_2>
"""

from pydantic import BaseModel, Field
from typing import List, Callable
from llm_patch_driver.llm.google_adapters import GoogleGenAiAdapter
from llm_patch_driver.llm.schemas import Message


TASK_PROMPT = TEST_STRING_PROMPT.format(
    TEXT_LENGTH=TEXT_LENGTH,
    SECTIONS=SECTIONS,
    WEIRD_CONDITION=WEIRD_CONDITION
)

messages = [
    {
        "role": "user",
        "parts": [{"text": TASK_PROMPT}]
    },
    {
        "role": "model",
        "parts": [{"text": DOC}]
    }
]
    

async def validation_string_condition(current_doc: str, call_llm: Callable) -> str | None:
    
    class DetectedRuleViolation(BaseModel):
        reasoning: str = Field(description="The reasoning why the rule was violated.")
        violation_description: str = Field(description="The description of the violation.")

    class Reflection(BaseModel):
        broken_rules: List[DetectedRuleViolation] | None = Field(description="The list of rules that were violated. If no rules were violated, return None.")

    reflection_prompt = REFLECTION_PROMPT.format(
        DOCUMENT=current_doc,
        SECTIONS=SECTIONS,
        WEIRD_CONDITION=WEIRD_CONDITION
    )

    violations = []
    
    if len(current_doc.split()) != TEXT_LENGTH:
        violations.append(DetectedRuleViolation(
            reasoning=f"The text is {len(current_doc.split())} words long. It should be {TEXT_LENGTH} words long.",
            violation_description=f"The text must be exactly {TEXT_LENGTH} words long."
        ))

    adapter = GoogleGenAiAdapter()

    llm_inputs = adapter.format_llm_call_input(
        messages=[Message(role="user", content=reflection_prompt)],
        schema=Reflection
    )

    response = adapter.parse_llm_output(call_llm(**llm_inputs, model="gemini-2.5-pro"))

    if response.attached_object and isinstance(response.attached_object, Reflection):
        if response.attached_object.broken_rules:
            violations.extend(response.attached_object.broken_rules)
        
    if violations:
        str_violations = "\n".join([f"{violation.reasoning}: {violation.violation_description}" for violation in violations])
        return str_violations
    
    else:
        return None