#########
PyCap-MFR
#########

**Py**\ thonRED\ **Cap-M**\ issing\ **F**\ ield\ **R**\ eporter
(**PyCap-MFR**) is a Python package which aims to extend the base
functionality of the `Blank values` rule in the `Data Quality` module on
**REDCap**.

Background
==========

The `Blank values` rule is designed to generate a report of all missing
fields in a **REDCap** project for one or more records, across
all `Data Access Groups` (**DAGs**); if applicable.

However, there are some limitations to the current implementation of
this rule on REDCap which make it unsuitable for some project and field
design implementations.
Currently, the `Blank values` rule considers a field as missing if:

#. The field is visible in the instrument.

   * i.e. the field has no branching logic, or the branching logic
     evaluates to `True`.

#. The event column where the field is located has some other data
   entered.

   * i.e. Can be in the same, or a unique instrument compared to the one
     where the "missing" field is located.
 
However, the current implementation of the rule places restrictions on
the field and project design for which it will provide accurate results.
Namely:

#. If condition `1` above is valid, due to condition `2`, the rule will
   report all fields without data in an instrument as missing, even if
   the instrument is not expected to have data for the given timepoint.

   * i.e. A `Witdrawal` or `Complications` instrument which may not
     have reportable data for all timepoints.

#. The rule does not properly evaluate condition `1` for fields which
   have been embedded in another field.

   * i.e. An embedded field is not visible in **REDCap** if its parent
     field is not visible, even if the embedded field's branching logic
     evaluates to `True`.
   * This means that embedded fields which are hidden due to the
     branching logic of their parent, but have either no branching
     logic or branching logic which evaluates to `True` themselves, are
     being incorrectly reported as missing.

#. The `Blank values` report has a maximum of `15 000` fields.

   * Especially when combined with the above limitations, the hard limit
     on number of fields means that the rule fails to provide a complete
     report of missing fields depending on the project design and the
     number of total records.
   * The incomplete reporting also precludes the use of external tools
     to generate a complete report of missing fields using the 
     intermediate export without significant additional manual work.

Current Limitations
===================

This section is **not** considered exhaustive, but highlights the known
limitations with the current implementation of `PyCap-MFR`.
Some limitations may be addressed in future versions of the package.

1. Incorrectly reports actually "Hidden" fields as "Missing" if an
   otherwise visible field is embedded in a section header that is not
   visible.

2. *May* incorrectly calculate the visibility of an embedded field if
   the embedded field is embedded in the "choice label" of a
   `radio button` or `checkbox` field, which *itself* is embedded in
   another field.

3. Incorrectly reports actually "Hidden" fields as "Missing" if the
   field is in an instrument which is hidden completely using
   **REDCap's** `Form Display Logic` feature.

4. Does not account for fields hidden using **REDCap's** `Action Tags`.

   * e.g. `@HIDDEN`, `@HIDDEN-SURVEY`, etc.

5. Cannot evaluate branching logic that uses **REDCap's**:

   * `Action Tags`: e.g. `@HIDDEN`, `@IF`, `@CALCDATE`, etc.
   * `Special Functions`: e.g. `if()`, `isblankormissingcode()`, etc.
   * `Smart Variables`: e.g. `[event-name]`, `[admission_arm_1]`, etc.
   