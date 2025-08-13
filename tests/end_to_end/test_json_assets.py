# Pydantic imports
from pydantic import BaseModel, Field, model_validator, EmailStr
import re
from typing import List
import json

TRANSCRIPT = """
**MS. GRANT (Board Chair):** All right, we're moving to the main item, which is our organizational structure. Mike, you said you wanted to talk through it, so, the floor's yours.

**MR. POPONDOPULOS (CEO):** Yeah, thanks, Leslie. So, okay, right, company structure, Bay Area Oil Drilling. Well, let's see… I think I'll just start at the top, but honestly, there's no real “top,” it's more like a bunch of really overcaffeinated triangles with people running around, but anyway, so, there's me, obviously, and, you know, I've got my assistant, Rachel—oh, not to be confused with the other Rachel, the one in Geology, who's got the curly hair, you know, the one who brings that weird fermented tea to meetings, not important.

So, underneath me, right, so we've got the core exec team. That's Carla—Carla in Finance, she's the one always telling me not to buy more drones for the field ops, which, honestly, if you ever saw our drone budget, it's… I mean, we'll get to Ops, but Carla, yeah, and then there's Victor—he's in Legal, and he's got that thing with the Star Trek mugs, and then, uh, Lila, she's running HR now. Oh! And Peter, our new CTO—I almost forgot him, which is wild because he emails me all the time about the ERP migration that's, frankly, never going to finish, but let's pretend it might.

Anyway, under Carla in Finance—well, actually, I should say, under Lila in HR, because that's where all the drama happens—no, but seriously, HR is like, what, a dozen people now? Maybe fourteen? Because we brought in that new DEI officer, Michelle, the one from Chevron—she's got opinions, and, honestly, she's right, but, like, it's a lot. So, in HR, we've got Lila, Michelle, obviously, and then you have two recruiters—Paul and Sam, not the Sam from Logistics, different Sam. Paul's the one with the dog. And then the benefits team, which, you know, is basically just Linda and Marcus, although Marcus is barely ever at his desk because he's always at the dentist—no idea what's going on there.

Wait, sorry, I should have mentioned—before I get too far off, on the exec side, there's also Operations, which, honestly, is like half the company. So, Laura is running Field Operations, she came over from Conoco, and she brought, like, five people with her, which is a whole thing, but anyway, Laura, and then her deputies—Kendrick, the tall one with the beard, and Sandeep, who actually knows how to drive the drill rigs, which is apparently not as common as you'd think, and then, um, where was I? Oh, right, their teams. So Laura's team is, what, I want to say about twenty-seven people? Maybe twenty-eight if you count the new techs, the ones who keep crashing the pickups.

Actually, back to Finance real quick—Carla's got two controllers, Greg and Emily, and then Emily's assistant, Tessa, and then the whole AP/AR squad, which is, what, I think there's six now? Because they just hired that guy from Texas, Jorge, who's got a thing for spreadsheets and brought his own chair? You know, if you've seen him, you'd know. Also, on payroll, we finally replaced Amanda, so that's four people there, not including the intern, Aidan, who I think is still in school, but I haven't checked.

Where was I? Sorry, I lost my notes. Oh, right, so IT. Peter's team, CTO, right, so he's got a bunch of engineers—well, DevOps, so there's Kevin and Shilpa, and the security lead, Marcus—not to be confused with Marcus from Benefits. This Marcus is the one who's always wearing that hoodie. And then, uh, I think four more engineers? Let's see—Ali, Zach, Priya, and that new guy, Lucas, who works remote from Idaho, which is weird because, why Idaho? Anyway, the IT helpdesk is under them, so that's, what, three people—Jess, Tom, and that really tall guy, Trevor, who fixed my laptop last week.

Operations, okay, I need to go back because under Laura there's also Logistics, and that's where things get weird. So, Logistics is headed by Sharon—she has three supervisors: Big Mike (not me, the other one), Destiny, and Chris. Each of them, honestly, they could run their own department, but we keep them in Logistics for now. Big Mike, he handles the fleet, which is… I think there are eight drivers? I want to say eight, maybe nine because we have that temp, Shaun, who's technically still in onboarding. And then there's warehouse, managed by Destiny, with four warehouse techs—Lamar, Nick, Eileen, and Rosa. Chris, he's the guy who handles supply chain contracts—he's got two assistants, both named David, and honestly I can't keep them straight, one of them is “tall David,” but I never remember which.

Legal, oh man, Victor. He's got three paralegals—Erica, Sung, and Dev. Erica's the one who always wears red. Sung just joined, super sharp. Dev's on paternity leave, but still CC'd on every email, which is impressive. And Victor's team also has the compliance officer, Julia, and the risk manager, Brian—he's the one who made us rewrite the evacuation plan for, like, the tenth time.

Marketing! I almost forgot about Marketing. Okay, so, headed by Jasmine. She used to run brand at a brewery, so now she's all about “earth tones.” Jasmine's got two designers—Will, with the skateboard, and Mandy, she does the digital stuff, and then there's three content people, all of whom are named something starting with S. Sarah, Sean, and Shira. Sarah's the one who actually posts on social, Sean mostly writes blog posts no one reads, and Shira, she's the new one, still learning the ropes. And then Jasmine also pulled in a data analyst from Sales, which was a whole HR paperwork situation, so now Peter in IT is mad because he lost his best Power BI person.

Board, am I missing… Oh, right, I didn't mention Geology. I always forget Geology, which is hilarious because half the company would fall into a sinkhole without them. So, Geology, that's Dr. Nguyen, who's basically the only reason we still have permits. She's got, let's see, three geologists—Rachel (the one with the tea), Benny, and Fahim, plus two junior geotechs, Julia and Andrew. Andrew's the one who broke the spectrometer, but he swears it wasn't him. They also have three field assistants, whose names I'm completely blanking on, but one of them has purple hair, I think it's Kayla.

Okay, so, above all these folks, you've got the VPs—so that's Carla, Laura, Peter, Victor, Jasmine, Dr. Nguyen. Wait, no, Dr. Nguyen's not a VP, she's a Director, but she should be a VP, but we haven't fixed the org chart. Anyway, there's, like, a senior leadership layer—what is that, Level 2? So me, then the execs, then VPs, then Directors, then Managers, then the rest. Or maybe that's four levels, unless you count the project leads, in which case that's five. I don't know, org charts are a scam.

Field Safety, can't forget them. After the big spill last year—remember that? So, Safety's got six people now: Amanda leads, with two site supervisors, Mo and Jeff, and then three safety techs—Irina, Boris, and Olivia. Olivia is the one who gives out the most citations, I swear she's got a badge quota. Amanda's also got that new hire, Henry, who transferred from Environmental, which, oh! Environmental, that's a new department, we spun it up after the EPA thing, so that's, uh, Wendy, head of Environmental, she came from the county, and her team is three people: Luis, Carla (not Finance Carla), and Mei. They do audits, mostly, and give me grief about recycling.

Sales, yeah, almost forgot, which is funny because they remind me whenever their bonuses are late. Sales is headed by Tommy, he's got five account execs—Sandra, Paul (again, not the recruiter Paul), Maggie, Raj, and Felipe. Maggie's the one with all the Chevron contacts, and Raj is, well, he's got a knack for landing the strangest accounts. Then there are two sales ops analysts—Ginny and Olivia. Different Olivia from Safety. Actually, three sales ops people now, because we hired Dan last week, and I haven't even met him yet.

Procurement—this is a whole saga. Procurement is run by Gina, she's, uh, what do you call it, queen of paperwork. She's got two buyers, Lisa and Gordon, and three contract admins: James, Mary, and Owen. Owen, the one with the cats. Don't ask. And then, uh, there's the inventory manager, Jacob, he reports to Gina too.

I feel like I missed something. Oh! R&D. We actually have an R&D team now. Small, but growing. Led by Dr. Roberts, with two research engineers, Priya and Hassan, plus a data scientist, Nikhil. Nikhil's the one who gave the all-hands talk about predictive maintenance and nobody understood a word, except Peter, who got really excited and tried to build his own version in Python.

Wait, is that eleven departments? Let me think—HR, Finance, IT, Ops, Logistics, Legal, Marketing, Geology, Field Safety, Environmental, Sales, Procurement, R\&D—oh, that's twelve. We dropped Drilling Engineering into Ops, though, so that doesn't count separately. Oh, Drilling. So, lead engineer is Travis, he's got a team of, I want to say, eight? No, nine if you count that intern, Zoe. Most of them just go by their last names—Gonzales, Lin, Schmidt, Carter, Patel, Nguyen (no relation to Dr. Nguyen), Silva, Lee. And Zoe, the intern. Most of them live out of their trucks.

Let's see, levels—so, execs, VPs, Directors, Managers, Leads, then the, you know, rank and file, but don't tell them I said that, they'll unionize. We have about—what did the last headcount say?—eighty-eight, no, seventy-three, seventy-six? It keeps changing. But at least seventy folks I can name, and a few more I forget at happy hour.

Oh, board, did I skip Compliance? That's under Legal, technically, but Julia in Compliance thinks she should be her own department, but for now, she and Brian and that temp, Eric, sit with Victor. Also, can I just say, if you try to make an org chart of this place, you'll need a whole whiteboard and three colors of marker.

**MS. GRANT:** Thank you, Mike. Just for clarity, can you remind us who reports directly to you?

**MR. POPONDOPULOS:** Uh, sure, yeah. So, direct reports, there's Carla (Finance), Victor (Legal/Compliance), Peter (IT), Lila (HR), Laura (Ops), Jasmine (Marketing), Tommy (Sales), Gina (Procurement), Wendy (Environmental), Amanda (Field Safety)—wait, no, Amanda's under Ops, but I talk to her directly about, you know, OSHA stuff, so, like, semi-direct. And Dr. Nguyen, technically she's a Director, so she reports to Laura, but I keep pulling her into strategy meetings. So, let's call it eleven direct reports, plus, you know, Rachel, my assistant, who's really the boss, honestly.

**MR. CHEN (Board Member):** Mike, could you clarify the reporting lines in Field Operations? You mentioned a Laura, but then several other names.

**MR. POPONDOPULOS:** Yeah, absolutely. Laura runs Field Ops—she's the VP, so under her, Kendrick and Sandeep are her deputies. Under Kendrick, you've got the drilling crews—Travis is the lead engineer, then his team—Gonzales, Lin, Schmidt, Carter, Patel, Nguyen, Silva, Lee, Zoe. Sandeep manages maintenance and site logistics, so he's got three supervisors, and then, uh, Destiny and Chris from Logistics, they both dual-report for special projects. I know, it's messy. Each crew has its own techs and assistants—oh, the new guys, I forgot, Ethan and Martin just started last week. Laura likes to keep it flat, but with seventy people it's like herding cats.

**MS. JAMES (Board Member):** Mike, what about Diversity, Equity, and Inclusion? Who leads that?

**MR. POPONDOPULOS:** Oh, right, Michelle! Yes, DEI is part of HR, so she's got a dotted line to Lila, but honestly she just talks to everyone. Michelle's team is, uh, two people—Aisha and Carlos. Carlos is part-time, but he runs those lunch seminars with the giant whiteboard, you know, the one with the “How Not To Get Sued” series? That's them.

Did I forget anyone? Oh, the cafeteria staff! Technically they're Facilities, but Facilities is a contractor now, except for Ed and Julia—different Julia from Compliance. They run the day-to-day stuff.

**MS. GRANT:** Thank you, Mike. Do we have any further clarifying questions from the board?

**MR. RIVERA:** Mike, you mentioned twelve departments, but I think the last count was eleven. Can you confirm how many departments and if there are any plans to consolidate?

**MR. POPONDOPULOS:** Good catch! Yeah, so, Legal and Compliance are sort of smooshed together. Drilling Engineering is part of Ops, so it's not a standalone department anymore. R\&D is technically its own thing now because the board wanted more innovation, but they used to be part of IT. So, yes, we have eleven main departments, with some overlap. And, yes, I keep talking about consolidating, but you try convincing Gina and Jasmine to share a team. Not in my lifetime.

**MS. GRANT:** Thank you, Mike. Unless there are more questions, I think that gives us a, well, colorful overview of Bay Area Oil Drilling's org structure.

**MR. POPONDOPULOS:** Yeah, sorry, I know it's a mess. But that's how you know it works, right? If everything made sense, we wouldn't be making money.

**MS. GRANT:** Thank you, Mike. All right, let's move on to the next agenda item.
"""

PHONE_BOOK = [
  {
    "first_name": "Mike",
    "last_name": "Popondopulos",
    "address": "500 Howard St, Suite 1200, San Francisco, CA 94105",
    "phone_number": "415-555-1001",
    "email": "mike.popondopulos@baod.com"
  },
  {
    "first_name": "Rachel",
    "last_name": "Mooney",
    "address": "720 Mission St, Apt 21D, San Francisco, CA 94103",
    "phone_number": "415-555-1022",
    "email": "rachel.mooney@baod.com"
  },
  {
    "first_name": "Carla",
    "last_name": "Gonzalez",
    "address": "880 7th Ave, Oakland, CA 94606",
    "phone_number": "510-555-2301",
    "email": "carla.gonzalez@baod.com"
  },
  {
    "first_name": "Victor",
    "last_name": "Saldana",
    "address": "221 Embarcadero Rd, Palo Alto, CA 94301",
    "phone_number": "650-555-1412",
    "email": "victor.saldana@baod.com"
  },
  {
    "first_name": "Lila",
    "last_name": "Chang",
    "address": "394 Castro St, Mountain View, CA 94041",
    "phone_number": "650-555-8855",
    "email": "lila.chang@baod.com"
  },
  {
    "first_name": "Peter",
    "last_name": "Thorne",
    "address": "102 Main St, Redwood City, CA 94063",
    "phone_number": "650-555-6623",
    "email": "peter.thorne@baod.com"
  },
  {
    "first_name": "Laura",
    "last_name": "Rivas",
    "address": "19 Beach Dr, Richmond, CA 94801",
    "phone_number": "510-555-3547",
    "email": "laura.rivas@baod.com"
  },
  {
    "first_name": "Jasmine",
    "last_name": "Shah",
    "address": "77 Lombard St, San Francisco, CA 94111",
    "phone_number": "415-555-7282",
    "email": "jasmine.shah@baod.com"
  },
  {
    "first_name": "Dr.",
    "last_name": "Nguyen",
    "address": "4100 El Camino Real, Apt 505, Palo Alto, CA 94306",
    "phone_number": "650-555-3200",
    "email": "nguyen.geology@baod.com"
  },
  {
    "first_name": "Michelle",
    "last_name": "Evans",
    "address": "1234 Franklin St, Apt 4B, Oakland, CA 94612",
    "phone_number": "510-555-9911",
    "email": "michelle.evans@baod.com"
  },
  {
    "first_name": "Amanda",
    "last_name": "Fields",
    "address": "2450 Telegraph Ave, Berkeley, CA 94704",
    "phone_number": "510-555-8765",
    "email": "amanda.fields@baod.com"
  },
  {
    "first_name": "Wendy",
    "last_name": "Sun",
    "address": "980 Oak Grove Ave, Menlo Park, CA 94025",
    "phone_number": "650-555-4433",
    "email": "wendy.sun@baod.com"
  },
  {
    "first_name": "Tommy",
    "last_name": "Duarte",
    "address": "1110 Polk St, San Francisco, CA 94109",
    "phone_number": "415-555-1127",
    "email": "tommy.duarte@baod.com"
  },
  {
    "first_name": "Gina",
    "last_name": "Obrien",
    "address": "3300 Laguna Ave, Oakland, CA 94602",
    "phone_number": "510-555-7000",
    "email": "gina.obrien@baod.com"
  },
  {
    "first_name": "Travis",
    "last_name": "Gonzales",
    "address": "800 Industrial Rd, San Carlos, CA 94070",
    "phone_number": "650-555-2122",
    "email": "travis.gonzales@baod.com"
  },
  {
    "first_name": "Kendrick",
    "last_name": "Steele",
    "address": "1919 Grand Ave, Alameda, CA 94501",
    "phone_number": "510-555-3255",
    "email": "kendrick.steele@baod.com"
  },
  {
    "first_name": "Sandeep",
    "last_name": "Mehra",
    "address": "2995 Middlefield Rd, Palo Alto, CA 94306",
    "phone_number": "650-555-7349",
    "email": "sandeep.mehra@baod.com"
  },
  {
    "first_name": "Jorge",
    "last_name": "Reyes",
    "address": "901 Webster St, Oakland, CA 94607",
    "phone_number": "510-555-1337",
    "email": "jorge.reyes@baod.com"
  },
  {
    "first_name": "Sarah",
    "last_name": "Kim",
    "address": "230 Divisadero St, San Francisco, CA 94117",
    "phone_number": "415-555-9801",
    "email": "sarah.kim@baod.com"
  },
  {
    "first_name": "Erica",
    "last_name": "Zhang",
    "address": "509 Lincoln Ave, San Jose, CA 95126",
    "phone_number": "408-555-2944",
    "email": "erica.zhang@baod.com"
  },
  {
    "first_name": "Kevin",
    "last_name": "Patel",
    "address": "1725 Willow St, San Jose, CA 95125",
    "phone_number": "408-555-8880",
    "email": "kevin.patel@baod.com"
  }
]

COMP = """
| Name              | Base Salary | Bonus    | Stock (Current Value) |
| ----------------- | ----------- | -------- | --------------------- |
| Mike Popondopulos | \$410,000   | \$60,000 | \$1,900,000           |
| Carla Gonzalez    | \$245,000   | \$30,000 | \$650,000             |
| Peter Thorne      | \$285,000   | \$50,000 | \$880,000             |
| Laura Rivas       | \$195,000   | \$22,500 | \$400,000             |
| Jasmine Shah      | \$172,000   | \$18,000 | \$320,000             |
| Kendrick Steele   | \$147,000   | \$17,000 | \$120,000             |
| Sandeep Mehra     | \$143,000   | \$14,500 | \$90,000              |
| Michelle Evans    | \$129,000   | \$8,000  | \$85,000              |
| Travis Gonzales   | \$138,000   | \$12,000 | \$108,000             |
| Victor Saldana    | \$233,000   | \$24,000 | \$500,000             |
| Amanda Fields     | \$118,000   | \$6,000  | \$40,000              |
| Dr. Nguyen        | \$207,000   | \$25,000 | \$325,000             |
| Jorge Reyes       | \$92,000    | \$3,500  | \$15,000              |
| Gina Obrien       | \$154,000   | \$10,000 | \$60,000              |
| Rachel Mooney     | \$104,000   | \$4,000  | \$5,000               |
"""


TEST_JSON_PROMPT = """
From a transcript of a meeting, contact information, and compensation information, extract all data about the organization structure for a company called "Bay Area Oil Drilling, Inc."

1. All employees that are mentioned in the transcript by name should be included in the output.
2. If compensation information is not provided, the compensation should be set to None.
3. If contact information is not provided, the contact should be set to None.

The output should be a valid JSON object that can be parsed by the model_validate function.

<transcript>
{TRANSCRIPT}
</transcript>

<compensation>
{COMP}
</compensation>

<contacts>
```json
{CONTACTS}
```
</contacts>

<schema>
```json
{SCHEMA}
```
</schema>
"""


# ---------------------------------------------------------------------------
# Data Models with Validation Logic
# ---------------------------------------------------------------------------


class Contact(BaseModel):
    """Contact information for a person.

    Email must be a valid e-mail address (handled by EmailStr).
    Phone numbers are validated against the common US pattern 000-000-0000.
    """

    email: EmailStr

    phone: str

    @model_validator(mode="after")
    def validate_phone(cls, contact):
        pattern = re.compile(r"^\d{3}-\d{3}-\d{4}$")
        if not pattern.match(contact.phone):
            raise ValueError(f"Invalid phone number format: {contact.phone}")
        return contact

class Address(BaseModel):
    street: str | None = None
    city: str
    state: str
    zip: str | None = None

class DepartmentInfo(BaseModel):
    department_name: str
    employee_title: str | None = None
    manager_name: str | None = None

class Salary(BaseModel):
    base_salary: int
    bonus: int
    stock_options: int
    total: int

    @model_validator(mode="after")
    def validate_total(cls, salary):
        """Ensure that *total* equals base + bonus + stock options."""
        expected = salary.base_salary + salary.bonus + salary.stock_options
        if salary.total != expected:
            raise ValueError(
                f"Salary total {salary.total} does not match its components "
                f"{salary.base_salary} + {salary.bonus} + {salary.stock_options} = {expected}"
            )
        return salary

class Employee(BaseModel):
    first_name: str
    last_name: str | None = None
    personal_contact: Contact | None = None
    work_contact: Contact | None = None
    address: Address | None = None
    department: DepartmentInfo
    compensation: Salary | None = None
    subordinates: List['Employee'] = Field(default_factory=list)
    distance_from_CEO: int

class Company(BaseModel):
    name: str
    address: Address | None = None
    CEO: Employee
    avg_compensation: int
    num_of_departments: int

    # Helper to recursively traverse the org-chart
    @staticmethod
    def _traverse_emp(emp, depth: int, seen: set, depts: dict, salary_stats: dict):
        # Ensure employee uniqueness (by first & last name)
        emp_key = (emp.first_name, emp.last_name)
        if emp_key in seen:
            raise ValueError(f"Duplicate employee detected: {emp_key}")
        seen.add(emp_key)

        # Validate distance_from_CEO – it is the index of the level in the hierarchy
        # starting at the CEO as 0, direct reports as 1, then 2, etc.
        expected_distance = depth
        if emp.distance_from_CEO != expected_distance:
            raise ValueError(
                f"Employee {emp.first_name} {emp.last_name or ''} has distance_from_CEO="
                f"{emp.distance_from_CEO}, expected {expected_distance}"
            )

        # Department consistency
        dept_name = emp.department.department_name
        mgr_name = emp.department.manager_name
        if dept_name in depts:
            current_mgr = depts[dept_name]
            # All employees in the same department must share the same manager name.
            if current_mgr is not None and mgr_name is not None and current_mgr != mgr_name:
                raise ValueError(
                    f"Department '{dept_name}' has inconsistent manager names: "
                    f"'{current_mgr}' vs '{mgr_name}'"
                )
            # Prefer non-None manager name when encountered.
            if current_mgr is None:
                depts[dept_name] = mgr_name
        else:
            depts[dept_name] = mgr_name

        # Salary aggregation
        if emp.compensation is not None:
            salary_stats["total_sum"] += emp.compensation.total
            salary_stats["count"] += 1

        # Recurse into subordinates
        for sub in emp.subordinates:
            Company._traverse_emp(sub, depth + 1, seen, depts, salary_stats)

    @model_validator(mode="after")
    def validate_company(cls, company):
        seen_employees: set = set()
        departments: dict = {}
        salary_stats = {"total_sum": 0, "count": 0}

        # Traverse entire org starting from CEO
        Company._traverse_emp(company.CEO, 0, seen_employees, departments, salary_stats)

        # avg_compensation must equal arithmetic mean of known salaries
        if salary_stats["count"]:
            avg_calculated = int(salary_stats["total_sum"] / salary_stats["count"])
            if company.avg_compensation != avg_calculated:
                raise ValueError(
                    f"avg_compensation {company.avg_compensation} does not match calculated "
                    f"average {avg_calculated}"
                )

        # num_of_departments must equal number of unique department names
        if company.num_of_departments != len(departments):
            raise ValueError(
                f"num_of_departments {company.num_of_departments} does not equal "
                f"unique departments count {len(departments)}"
            )

        return company


# ---------------------------------------------------------------------------
# JSON that doesn't pass model_validate
# ---------------------------------------------------------------------------

TEST_JSON = {
  "name": "Bay Area Oil Drilling, Inc.",
  "address": None,
  "CEO": {
    "first_name": "Mike",
    "last_name": "Popondopulos",
    "personal_contact": None,
    "work_contact": {
      "email": "mike.popondopulos@baod.com",
      "phone": "415-555-1001"
    },
    "address": {
      "street": "500 Howard St, Suite 1200",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94105"
    },
    "department": {
      "department_name": "Executive",
      "employee_title": "Chief Executive Officer",
      "manager_name": None
    },
    "compensation": {
      "base_salary": 410000,
      "bonus": 60000,
      "stock_options": 1900000,
      "total": 2370000
    },
    "distance_from_CEO": 0,
    "subordinates": [
      {
        "first_name": "Rachel",
        "last_name": "Mooney",
        "personal_contact": None,
        "work_contact": {
          "email": "rachel.mooney@baod.com",
          "phone": "415-555-1022"
        },
        "address": {
          "street": "720 Mission St, Apt 21D",
          "city": "San Francisco",
          "state": "CA",
          "zip": "94103"
        },
        "department": {
          "department_name": "Executive",
          "employee_title": "Executive Assistant",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 104000,
          "bonus": 4000,
          "stock_options": 5000,
          "total": 113000
        },
        "distance_from_CEO": 1,
        "subordinates": []
      },
      {
        "first_name": "Carla",
        "last_name": "Gonzalez",
        "personal_contact": None,
        "work_contact": {
          "email": "carla.gonzalez@baod.com",
          "phone": "510-555-2301"
        },
        "address": {
          "street": "880 7th Ave",
          "city": "Oakland",
          "state": "CA",
          "zip": "94606"
        },
        "department": {
          "department_name": "Finance",
          "employee_title": "VP of Finance",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 245000,
          "bonus": 30000,
          "stock_options": 650000,
          "total": 925000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Greg",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Finance",
              "employee_title": "Controller",
              "manager_name": "Carla Gonzalez"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Emily",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Finance",
              "employee_title": "Controller",
              "manager_name": "Carla Gonzalez"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": [
              {
                "first_name": "Tessa",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "Finance",
                  "employee_title": "Assistant",
                  "manager_name": "Emily"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              }
            ]
          },
          {
            "first_name": "Jorge",
            "last_name": "Reyes",
            "personal_contact": None,
            "work_contact": {
              "email": "jorge.reyes@baod.com",
              "phone": "510-555-1337"
            },
            "address": {
              "street": "901 Webster St",
              "city": "Oakland",
              "state": "CA",
              "zip": "94607"
            },
            "department": {
              "department_name": "Finance",
              "employee_title": "AP/AR",
              "manager_name": "Carla Gonzalez"
            },
            "compensation": {
              "base_salary": 92000,
              "bonus": 3500,
              "stock_options": 15000,
              "total": 110500
            },
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Aidan",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Finance",
              "employee_title": "Payroll Intern",
              "manager_name": "Carla Gonzalez"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Victor",
        "last_name": "Saldana",
        "personal_contact": None,
        "work_contact": {
          "email": "victor.saldana@baod.com",
          "phone": "650-555-1412"
        },
        "address": {
          "street": "221 Embarcadero Rd",
          "city": "Palo Alto",
          "state": "CA",
          "zip": "94301"
        },
        "department": {
          "department_name": "Legal/Compliance",
          "employee_title": "VP of Legal",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 233000,
          "bonus": 24000,
          "stock_options": 500000,
          "total": 757000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Erica",
            "last_name": "Zhang",
            "personal_contact": None,
            "work_contact": {
              "email": "erica.zhang@baod.com",
              "phone": "408-555-2944"
            },
            "address": {
              "street": "509 Lincoln Ave",
              "city": "San Jose",
              "state": "CA",
              "zip": "95126"
            },
            "department": {
              "department_name": "Legal",
              "employee_title": "Paralegal",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Sung",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Paralegal",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Dev",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Paralegal",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Julia",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Compliance Officer",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Brian",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Risk Manager",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Eric",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Compliance Temp",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Lila",
        "last_name": "Chang",
        "personal_contact": None,
        "work_contact": {
          "email": "lila.chang@baod.com",
          "phone": "650-555-8855"
        },
        "address": {
          "street": "394 Castro St",
          "city": "Mountain View",
          "state": "CA",
          "zip": "94041"
        },
        "department": {
          "department_name": "HR",
          "employee_title": "VP of HR",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Paul",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "HR",
              "employee_title": "Recruiter",
              "manager_name": "Lila Chang"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Sam",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "HR",
              "employee_title": "Recruiter",
              "manager_name": "Lila Chang"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Linda",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "HR",
              "employee_title": "Benefits",
              "manager_name": "Lila Chang"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Marcus",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "HR",
              "employee_title": "Benefits",
              "manager_name": "Lila Chang"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Michelle",
            "last_name": "Evans",
            "personal_contact": None,
            "work_contact": {
              "email": "michelle.evans@baod.com",
              "phone": "510-555-9911"
            },
            "address": {
              "street": "1234 Franklin St, Apt 4B",
              "city": "Oakland",
              "state": "CA",
              "zip": "94612"
            },
            "department": {
              "department_name": "HR",
              "employee_title": "DEI Officer",
              "manager_name": "Lila Chang"
            },
            "compensation": {
              "base_salary": 129000,
              "bonus": 8000,
              "stock_options": 85000,
              "total": 222000
            },
            "distance_from_CEO": 2,
            "subordinates": [
              {
                "first_name": "Aisha",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "HR",
                  "employee_title": "DEI Team",
                  "manager_name": "Michelle Evans"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              },
              {
                "first_name": "Carlos",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "HR",
                  "employee_title": "DEI Team",
                  "manager_name": "Michelle Evans"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              }
            ]
          }
        ]
      },
      {
        "first_name": "Peter",
        "last_name": "Thorne",
        "personal_contact": None,
        "work_contact": {
          "email": "peter.thorne@baod.com",
          "phone": "650-555-6623"
        },
        "address": {
          "street": "102 Main St",
          "city": "Redwood City",
          "state": "CA",
          "zip": "94063"
        },
        "department": {
          "department_name": "IT",
          "employee_title": "CTO",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 285000,
          "bonus": 50000,
          "stock_options": 880000,
          "total": 1215000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Kevin",
            "last_name": "Patel",
            "personal_contact": None,
            "work_contact": {
              "email": "kevin.patel@baod.com",
              "phone": "408-555-8880"
            },
            "address": {
              "street": "1725 Willow St",
              "city": "San Jose",
              "state": "CA",
              "zip": "95125"
            },
            "department": {
              "department_name": "IT",
              "employee_title": "DevOps Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Shilpa",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "DevOps Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Marcus",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Security Lead",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Ali",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Zach",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Priya",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Lucas",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Jess",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Helpdesk",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Tom",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Helpdesk",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Trevor",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Helpdesk",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Laura",
        "last_name": "Rivas",
        "personal_contact": None,
        "work_contact": {
          "email": "laura.rivas@baod.com",
          "phone": "510-555-3547"
        },
        "address": {
          "street": "19 Beach Dr",
          "city": "Richmond",
          "state": "CA",
          "zip": "94801"
        },
        "department": {
          "department_name": "Operations",
          "employee_title": "VP of Operations",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 195000,
          "bonus": 22500,
          "stock_options": 400000,
          "total": 617500
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Kendrick",
            "last_name": "Steele",
            "personal_contact": None,
            "work_contact": {
              "email": "kendrick.steele@baod.com",
              "phone": "510-555-3255"
            },
            "address": {
              "street": "1919 Grand Ave",
              "city": "Alameda",
              "state": "CA",
              "zip": "94501"
            },
            "department": {
              "department_name": "Operations",
              "employee_title": "Deputy, Field Ops",
              "manager_name": "Laura Rivas"
            },
            "compensation": {
              "base_salary": 147000,
              "bonus": 17000,
              "stock_options": 120000,
              "total": 284000
            },
            "distance_from_CEO": 2,
            "subordinates": [
              {
                "first_name": "Travis",
                "last_name": "Gonzales",
                "personal_contact": None,
                "work_contact": {
                  "email": "travis.gonzales@baod.com",
                  "phone": "650-555-2122"
                },
                "address": {
                  "street": "800 Industrial Rd",
                  "city": "San Carlos",
                  "state": "CA",
                  "zip": "94070"
                },
                "department": {
                  "department_name": "Operations",
                  "employee_title": "Lead Drilling Engineer",
                  "manager_name": "Kendrick Steele"
                },
                "compensation": {
                  "base_salary": 138000,
                  "bonus": 12000,
                  "stock_options": 108000,
                  "total": 158000
                },
                "distance_from_CEO": 3,
                "subordinates": [
                  {
                    "first_name": "Gonzales",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Lin",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Schmidt",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Carter",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Patel",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Nguyen",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Silva",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Lee",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Zoe",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Intern",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  }
                ]
              },
              {
                "first_name": "Ethan",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "Operations",
                  "employee_title": "Field Tech",
                  "manager_name": "Kendrick Steele"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              },
              {
                "first_name": "Martin",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "Operations",
                  "employee_title": "Field Tech",
                  "manager_name": "Kendrick Steele"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              }
            ]
          },
          {
            "first_name": "Sandeep",
            "last_name": "Mehra",
            "personal_contact": None,
            "work_contact": {
              "email": "sandeep.mehra@baod.com",
              "phone": "650-555-7349"
            },
            "address": {
              "street": "2995 Middlefield Rd",
              "city": "Palo Alto",
              "state": "CA",
              "zip": "94306"
            },
            "department": {
              "department_name": "Operations",
              "employee_title": "Deputy, Maintenance & Logistics",
              "manager_name": "Laura Rivas"
            },
            "compensation": {
              "base_salary": 143000,
              "bonus": 14500,
              "stock_options": 90000,
              "total": 247500
            },
            "distance_from_CEO": 2,
            "subordinates": [
              {
                "first_name": "Sharon",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "Logistics",
                  "employee_title": "Logistics Manager",
                  "manager_name": "Sandeep Mehra"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": [
                  {
                    "first_name": "Big Mike",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Logistics",
                      "employee_title": "Fleet Supervisor",
                      "manager_name": "Sharon"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": [
                      {
                        "first_name": "Shaun",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Temp Driver",
                          "manager_name": "Big Mike"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      }
                    ]
                  },
                  {
                    "first_name": "Destiny",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Logistics",
                      "employee_title": "Warehouse Supervisor",
                      "manager_name": "Sharon"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": [
                      {
                        "first_name": "Lamar",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Warehouse Tech",
                          "manager_name": "Destiny"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      },
                      {
                        "first_name": "Nick",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Warehouse Tech",
                          "manager_name": "Destiny"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      },
                      {
                        "first_name": "Eileen",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Warehouse Tech",
                          "manager_name": "Destiny"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      },
                      {
                        "first_name": "Rosa",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Warehouse Tech",
                          "manager_name": "Destiny"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      }
                    ]
                  },
                  {
                    "first_name": "Chris",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Logistics",
                      "employee_title": "Supervisor",
                      "manager_name": "Sharon"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": [
                      {
                        "first_name": "David",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Contract Assistant",
                          "manager_name": "Chris"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      },
                      {
                        "first_name": "David",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Contract Assistant",
                          "manager_name": "Chris"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        "first_name": "Jasmine",
        "last_name": "Shah",
        "personal_contact": None,
        "work_contact": {
          "email": "jasmine.shah@baod.com",
          "phone": "415-555-7282"
        },
        "address": {
          "street": "77 Lombard St",
          "city": "San Francisco",
          "state": "CA",
          "zip": "94111"
        },
        "department": {
          "department_name": "Marketing",
          "employee_title": "VP of Marketing",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 172000,
          "bonus": 18000,
          "stock_options": 320000,
          "total": 510000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Will",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Marketing",
              "employee_title": "Designer",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Mandy",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Marketing",
              "employee_title": "Digital Designer",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Sarah",
            "last_name": "Kim",
            "personal_contact": None,
            "work_contact": {
              "email": "sarah.kim@baod.com",
              "phone": "415-555-9801"
            },
            "address": {
              "street": "230 Divisadero St",
              "city": "San Francisco",
              "state": "CA",
              "zip": "94117"
            },
            "department": {
              "department_name": "Marketing",
              "employee_title": "Content Specialist",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Sean",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Marketing",
              "employee_title": "Content Writer",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Shira",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Marketing",
              "employee_title": "Content Associate",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Dr.",
        "last_name": "Nguyen",
        "personal_contact": None,
        "work_contact": {
          "email": "nguyen.geology@baod.com",
          "phone": "650-555-3200"
        },
        "address": {
          "street": "4100 El Camino Real, Apt 505",
          "city": "Palo Alto",
          "state": "CA",
          "zip": "94306"
        },
        "department": {
          "department_name": "Geology",
          "employee_title": "Director of Geology",
          "manager_name": "Laura Rivas"
        },
        "compensation": {
          "base_salary": 207000,
          "bonus": 25000,
          "stock_options": 325000,
          "total": 557000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Rachel",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Geologist",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Benny",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Geologist",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Fahim",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Geologist",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Julia",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Junior Geotech",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Andrew",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Junior Geotech",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Kayla",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Field Assistant",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Amanda",
        "last_name": "Fields",
        "personal_contact": None,
        "work_contact": {
          "email": "amanda.fields@baod.com",
          "phone": "510-555-8765"
        },
        "address": {
          "street": "2450 Telegraph Ave",
          "city": "Berkeley",
          "state": "CA",
          "zip": "94704"
        },
        "department": {
          "department_name": "Field Safety",
          "employee_title": "Head of Field Safety",
          "manager_name": "Laura Rivas"
        },
        "compensation": {
          "base_salary": 118000,
          "bonus": 6000,
          "stock_options": 40000,
          "total": 164000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Mo",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Site Supervisor",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Jeff",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Site Supervisor",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Irina",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Safety Tech",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Boris",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Safety Tech",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Olivia",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Safety Tech",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Henry",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Safety Tech",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Wendy",
        "last_name": "Sun",
        "personal_contact": None,
        "work_contact": {
          "email": "wendy.sun@baod.com",
          "phone": "650-555-4433"
        },
        "address": {
          "street": "980 Oak Grove Ave",
          "city": "Menlo Park",
          "state": "CA",
          "zip": "94025"
        },
        "department": {
          "department_name": "Environmental",
          "employee_title": "Head of Environmental",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Luis",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Environmental",
              "employee_title": "Analyst",
              "manager_name": "Wendy Sun"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Carla",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Environmental",
              "employee_title": "Analyst",
              "manager_name": "Wendy Sun"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Mei",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Environmental",
              "employee_title": "Analyst",
              "manager_name": "Wendy Sun"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Tommy",
        "last_name": "Duarte",
        "personal_contact": None,
        "work_contact": {
          "email": "tommy.duarte@baod.com",
          "phone": "415-555-1127"
        },
        "address": {
          "street": "1110 Polk St",
          "city": "San Francisco",
          "state": "CA",
          "zip": "94109"
        },
        "department": {
          "department_name": "Sales",
          "employee_title": "Head of Sales",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Sandra",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Paul",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Maggie",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Raj",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Felipe",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Ginny",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Sales-Ops Analyst",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Olivia",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Sales-Ops Analyst",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Dan",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Sales-Ops Analyst",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Gina",
        "last_name": "Obrien",
        "personal_contact": None,
        "work_contact": {
          "email": "gina.obrien@baod.com",
          "phone": "510-555-7000"
        },
        "address": {
          "street": "3300 Laguna Ave",
          "city": "Oakland",
          "state": "CA",
          "zip": "94602"
        },
        "department": {
          "department_name": "Procurement",
          "employee_title": "Head of Procurement",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 154000,
          "bonus": 10000,
          "stock_options": 60000,
          "total": 224000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Lisa",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Buyer",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Gordon",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Buyer",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "James",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Contract Admin",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Mary",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Contract Admin",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Owen",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Contract Admin",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Jacob",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Inventory Manager",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Dr. Roberts",
        "last_name": None,
        "personal_contact": None,
        "work_contact": None,
        "address": None,
        "department": {
          "department_name": "R&D",
          "employee_title": "Head of R&D",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Priya",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "R&D",
              "employee_title": "Research Engineer",
              "manager_name": "Dr. Roberts"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Hassan",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "R&D",
              "employee_title": "Research Engineer",
              "manager_name": "Dr. Roberts"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Nikhil",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "R&D",
              "employee_title": "Data Scientist",
              "manager_name": "Dr. Roberts"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Ed",
        "last_name": None,
        "personal_contact": None,
        "work_contact": None,
        "address": None,
        "department": {
          "department_name": "Facilities",
          "employee_title": "Cafeteria",
          "manager_name": None
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": []
      },
      {
        "first_name": "Julia",
        "last_name": None,
        "personal_contact": None,
        "work_contact": None,
        "address": None,
        "department": {
          "department_name": "Facilities",
          "employee_title": "Cafeteria",
          "manager_name": None
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": []
      }
    ]
  },
  "avg_compensation": 495704,
  "num_of_departments": 11
}


from llm_patch_driver import PatchTarget, JsonPatch
from dataclasses import dataclass

@dataclass
class TestingJsonPatch:
    raw_json: dict
    some_attribute: str

json_target = PatchTarget(
    object=TestingJsonPatch(raw_json=TEST_JSON, some_attribute="test"), 
    validation_schema=Company,
    content_attribute="raw_json",
    patch_type=JsonPatch
)

user_prompt = TEST_JSON_PROMPT.format(
    TRANSCRIPT=TRANSCRIPT,
    COMP=COMP,
    CONTACTS=json.dumps(PHONE_BOOK),
    SCHEMA=Company.model_json_schema()
)

messages = [
    {
        "role": "user",
        "parts": [{"text": user_prompt}]
    },
    {
        "role": "model",
        "parts": [{"text": json.dumps(TEST_JSON)}]
    }
]
